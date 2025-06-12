# -*- coding: utf-8 -*-
"""
Dataset Query Generator

This script processes dataset metadata and generates research questions using LLMs.

Author: Junyong Lin
Date: 2025-06-12
Version: 1.0
"""

import os
import json
import shutil
import requests
import logging
from typing import Dict, List, Optional, Tuple, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class APIConfig:
    """Configuration for API settings"""
    
    def __init__(self):
        # Note: In production, use environment variables or secure config files
        self.api_keys = {
            'chatglm': 'YOUR_CHATGLM_API_KEY',
            'openai': 'YOUR_OPENAI_API_KEY'
        }
        self.base_url = "https://gpt-api.hkust-gz.edu.cn/v1/chat/completions"
        self.default_model = "gpt-4"
        self.temperature = 0.7


class DatasetQueryGenerator:
    """Main class for generating dataset-related queries using AI models"""
    
    def __init__(self, config: APIConfig):
        self.config = config
        self.api_usage_stats = {
            'total_consume': 0,
            'total_tokens': 0,
            'total_completion_tokens': 0,
            'total_prompt_tokens': 0
        }
    
    def send_api_request(self, system_content: str, user_content: str) -> Optional[Dict]:
        """
        Send request to AI API
        
        Args:
            system_content: System prompt content
            user_content: User prompt content
            
        Returns:
            API response as dictionary or None if error
        """
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.config.api_keys['openai']}"
        }
        
        data = {
            "model": self.config.default_model,
            "messages": [
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content},
            ],
            "temperature": self.config.temperature
        }
        
        try:
            response = requests.post(
                self.config.base_url, 
                headers=headers, 
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
    
    def get_relevant_question_types(self, dataset_description: str) -> Tuple[Dict, List[str]]:
        """
        Determine relevant question types for a dataset
        
        Args:
            dataset_description: Description of the dataset
            
        Returns:
            Tuple of (api_cost, question_types)
        """
        api_cost = {'completion_tokens': 0, 'prompt_tokens': 0, 'total_tokens': 0, 'consume': 0}
        
        system_content = """You are a researcher generating questions and answers to find relevant metadata, datasets, and papers within a specific domain. 
Below are the potential question types. Choose the type that best fits the field information and the user's purpose.

1. **Verification**: Verification questions seek a simple 'yes' or 'no' answer to confirm specific details.
2. **Disjunctive**: Disjunctive questions present multiple options, asking the researcher to identify which one is applicable.
3. **Concept Completion**: Concept completion questions start with 'Who?', 'What?', 'When?', or 'Where?' to prompt the identification or completion of a specific term or defined element.
4. **Example**: Example questions ask for instances that illustrate a particular scientific concept.
5. **Feature Specification**: Feature specification questions inquire about the properties or characteristics of a concept, object, or phenomenon.
6. **Quantification**: Quantification questions seek numerical or measurable information.
7. **Definition**: Definition questions ask researchers to explain the meaning of a specific term or concept.
8. **Comparison**: Comparison questions require researchers to identify similarities and/or differences between two or more scientific resources or concepts.
9. **Interpretation**: Interpretation questions ask researchers to infer underlying rules of their observed data patterns.
10. **Causal Antecedent**: Causal antecedent questions inquire about the reasons or causes behind an event, trend.
11. **Causal Consequence**: Causal consequence questions ask about the outcomes or results that follow from a specific event, trend.
12. **Goal Orientation**: Goal orientation questions investigate the objectives or intentions behind the creation of a dataset, publication, or research project.
13. **Instrumental/Procedural**: Instrumental or procedural questions ask how to achieve certain goals.
14. **Enablement**: Enablement questions focus on identifying the resources or conditions that enable an agent to perform a specific action.
15. **Expectation**: Expectation questions inquire about anticipated outcomes or reasons why expected results did not occur.
16. **Judgmental**: Judgmental questions ask researchers to express their opinions or evaluations.
17. **Assertion**: Assertion questions make a statement indicating lack of knowledge or understanding.
18. **Request/Directive**: Request or directive questions involve asking researchers to perform specific tasks, such as summarizing information, analyzing data, or conducting searches."""
        
        user_content = f"""Task: Based on the following dataset metadata, return the most appropriate 8 question types. Give me the name of each type and not other information.

**Dataset Metadata:** {dataset_description}"""
        
        response = self.send_api_request(system_content, user_content)
        if not response:
            return api_cost, []
        
        # Update API usage stats
        usage = response.get('usage', {})
        api_cost['consume'] += response.get('consume', 0)
        api_cost['total_tokens'] += usage.get('total_tokens', 0)
        api_cost['completion_tokens'] += usage.get('completion_tokens', 0)
        api_cost['prompt_tokens'] += usage.get('prompt_tokens', 0)
        
        # Extract question types from response
        generated_info = response['choices'][0].get('message', {}).get('content', '')
        question_types = [line.split('. ', 1)[1] for line in generated_info.split('\n') if '. ' in line]
        
        return api_cost, question_types
    
    def generate_questions_for_type(
        self, 
        dataset_description: str, 
        pdf_data: List[str], 
        question_type_info: Dict,
        questions_per_type: int = 3
    ) -> Optional[Dict]:
        """
        Generate questions for a specific question type
        
        Args:
            dataset_description: Dataset metadata description
            pdf_data: Extracted PDF content data
            question_type_info: Information about the question type
            questions_per_type: Number of questions to generate
            
        Returns:
            Generated questions and answers
        """
        system_content = """You are a researcher asking questions aiming to find relevant metadata, datasets, and papers within a specific domain."""
        
        # Choose content based on whether PDF data is available
        field_content = f"- **Metadata**: {dataset_description}"
        if pdf_data:
            field_content += f"\n- **Content of relevant Papers**: {pdf_data}"
        
        user_content = f"""I am exploring the field above. I'm interested in finding datasets or understanding data collection methods related to this field.
**Field:**
{field_content}

Please generate {"three questions" if questions_per_type == 3 else "one question"} that aim to discover or explore general information about data collection techniques, challenges, and potential datasets in this domain under the question type below and answer each query using the field above.

- **Question Type**: {question_type_info['Type']}
- **Question Description**: {question_type_info['Definition']}
- **Question Example**: {question_type_info['Examples']}

**Instructions:**
1. Only questions and answers without any other information.
2. Do not summarize the metadata{" or Content of relevant Papers" if pdf_data else ""}.
3. Focus on questions that are open-ended and explore a wide range of possibilities or methodologies related to the field.
4. Use neutral terms like "a dataset," "data collection method," or "research approach," instead of specific references like "the study," "this dataset" or "dataset mentioned".
5. Aim for questions that encourage exploration of nuanced technological details, methodological rigor, and potential sources or strategies for dataset expansion or refinement within the field.
6. The answer should come from the field I mentioned above.
7. Please provide the results in exactly the following json format:

"""
        
        # Response format based on number of questions
        if questions_per_type == 3:
            response_format = """[
  {
    "Question": "",
    "Answer": ""
  },
  {
    "Question": "",
    "Answer": ""
  },
  {
    "Question": "",
    "Answer": ""
  }
]"""
        else:
            response_format = """[
  {
    "Question": "",
    "Answer": ""
  }
]"""
        
        response = self.send_api_request(system_content, user_content + response_format)
        if not response:
            return None
        
        # Extract and parse the generated content
        generated_info = response['choices'][0].get('message', {}).get('content', '')
        
        try:
            # Clean and parse JSON response
            cleaned_data = generated_info.replace("```", "").replace("json", "").strip()
            json_data = json.loads(cleaned_data)
            return {
                'question_type': question_type_info['Type'],
                'questions': json_data,
                'api_usage': response.get('usage', {})
            }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return None
    
    def generate_query_pipeline(
        self, 
        dataset_description: str, 
        pdf_data: Optional[List[str]], 
        question_types_config: Dict,
        mode: str = 'full'
    ) -> Tuple[Dict, Dict]:
        """
        Main pipeline for generating queries
        
        Args:
            dataset_description: Dataset metadata description
            pdf_data: Extracted PDF content (optional)
            question_types_config: Configuration of question types
            mode: 'full' for all types, 'adaptive' for selected types
            
        Returns:
            Tuple of (api_costs, query_results_dict)
        """
        api_costs = {'completion_tokens': 0, 'prompt_tokens': 0, 'total_tokens': 0, 'consume': 0}
        query_results = {}
        
        if mode == 'adaptive':
            # Get relevant question types for the dataset
            type_costs, relevant_types = self.get_relevant_question_types(dataset_description)
            self._update_api_costs(api_costs, type_costs)
            
            # Filter question types based on relevance
            filtered_types = [
                qt for qt in question_types_config['QuestionTypes'] 
                if qt['Type'] in relevant_types
            ]
            questions_per_type = 1
        else:
            # Use all question types
            filtered_types = question_types_config['QuestionTypes']
            questions_per_type = 3
        
        # Generate questions for each type
        for question_type_info in filtered_types:
            result = self.generate_questions_for_type(
                dataset_description, 
                pdf_data or [], 
                question_type_info,
                questions_per_type
            )
            
            if result:
                query_results[result['question_type']] = result['questions']
                self._update_api_costs(api_costs, result['api_usage'])
        
        return api_costs, query_results
    
    def _update_api_costs(self, total_costs: Dict, new_costs: Dict):
        """Update total API costs with new costs"""
        for key in ['completion_tokens', 'prompt_tokens', 'total_tokens', 'consume']:
            total_costs[key] += new_costs.get(key, 0)
    
    @staticmethod
    def extract_metadata_structure(metadata: Dict) -> Dict:
        """
        Extract and structure metadata information
        
        Args:
            metadata: Raw metadata dictionary
            
        Returns:
            Structured metadata dictionary
        """
        return {
            "id": metadata["context"].get("metadataVO", {}).get("id", ""),
            "relatedPaper": 0,
            "context": {
                "metadata": {
                    "titleEn": metadata["context"].get("metadataVO", {}).get("titleEn", ""),
                    "description": metadata["context"].get("metadataWordVO", {}).get("description", ""),
                    "instructions": metadata["context"].get("metadataWordVO", {}).get("instructions", ""),
                    "east": metadata["context"].get("metadataVO", {}).get("east", ""),
                    "west": metadata["context"].get("metadataVO", {}).get("west", ""),
                    "south": metadata["context"].get("metadataVO", {}).get("south", ""),
                    "north": metadata["context"].get("metadataVO", {}).get("north", ""),
                    "startTime": metadata["context"].get("metadataVO", {}).get("startTime", ""),
                    "endTime": metadata["context"].get("metadataVO", {}).get("endTime", ""),
                    "fileSize": metadata["context"].get("metadataVO", {}).get("fileSize", ""),
                    "cstr": metadata["context"].get("metadataVO", {}).get("cstr", ""),
                    "doi": metadata["context"].get("metadataVO", {}).get("doi", ""),
                    "dataFormat": metadata["context"].get("metadataVO", {}).get("dataFormat", ""),
                    "license": metadata["context"].get("metadataVO", {}).get("license", ""),
                },
                "authorList": [
                    {
                        "nameEn": item.get("nameEn", ""),
                        "unitEn": item.get("unitEn", "")
                    }
                    for item in metadata["context"].get("authorVOList", [])
                ],
                "literatureList": [
                    f"{item.get('title', '')} + {item.get('reference', '')}"
                    for item in metadata["context"].get("literatureVOList", [])
                ],
                "keywordStandList": [
                    item.get('enName', '')
                    for item in metadata["context"].get("keywordStandVOList", [])
                ],
                "themeList": [
                    item.get('enName', '')
                    for item in metadata["context"].get("themeList", [])
                ],
                "placeKeywordList": [
                    item.get('keywordEn', '')
                    for item in metadata["context"].get("placeKeywordVOList", [])
                ],
                "temporalKeywordList": [
                    item.get('keywordEn', '')
                    for item in metadata["context"].get("temporalKeywordVOList", [])
                ],
                "projectList": [
                    item.get('titleEn', '')
                    for item in metadata["context"].get("projectVOList", [])
                ],
                "relatedDataList": [
                    item.get('titleEn', '')
                    for item in metadata["context"].get("relatedDataList", [])
                ],
            },
            "extract_pdfs_data": None,
            "query": {},
            "api_cost": None
        }


class DatasetProcessor:
    """Process datasets and generate queries"""
    
    def __init__(self, config_path: str):
        self.config = APIConfig()
        self.generator = DatasetQueryGenerator(self.config)
        self.question_types_config = self._load_question_types_config(config_path)
    
    def _load_question_types_config(self, config_path: str) -> Dict:
        """Load question types configuration from file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Question types config file not found: {config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise
    
    def process_single_dataset(
        self, 
        dataset_path: str, 
        output_path: str, 
        mode: str = 'full'
    ) -> bool:
        """
        Process a single dataset folder
        
        Args:
            dataset_path: Path to dataset folder
            output_path: Output file path
            mode: Processing mode ('full' or 'adaptive')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            dataset_id = os.path.basename(dataset_path)
            metadata_file = os.path.join(dataset_path, f"{dataset_id}.json")
            
            # Skip if output already exists
            if os.path.exists(output_path):
                logger.info(f"Output already exists, skipping: {output_path}")
                return True
            
            # Load metadata
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Extract dataset description
            title = metadata["context"]["metadataVO"].get("title", "")
            description = metadata["context"]["metadataVO"].get("description", "")
            dataset_description = f"{title}\n{description}"
            
            # Load PDF data if available (for full mode)
            pdf_data = []
            if mode == 'full':
                pdf_data = self._load_pdf_data(dataset_path, dataset_id)
            
            # Generate queries
            if (mode == 'full' and pdf_data) or mode == 'adaptive':
                data_structure = DatasetQueryGenerator.extract_metadata_structure(metadata)
                
                api_costs, query_results = self.generator.generate_query_pipeline(
                    dataset_description, 
                    pdf_data if mode == 'full' else None,
                    self.question_types_config,
                    mode
                )
                
                data_structure["query"] = query_results
                data_structure["api_cost"] = api_costs
                data_structure["relatedPaper"] = len(pdf_data) if pdf_data else 0
                data_structure["extract_pdfs_data"] = pdf_data if mode == 'full' else None
                
                # Save results
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data_structure, f, indent=4, ensure_ascii=False)
                
                logger.info(f"Successfully processed: {dataset_id}")
                return True
            else:
                logger.warning(f"No PDF data found for dataset: {dataset_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error processing dataset {dataset_path}: {e}")
            return False
    
    def _load_pdf_data(self, dataset_path: str, dataset_id: str) -> List[str]:
        """Load extracted PDF data from dataset folder"""
        pdf_data = []
        
        for filename in os.listdir(dataset_path):
            if filename != f"{dataset_id}.json":
                pdf_file_path = os.path.join(dataset_path, filename)
                try:
                    with open(pdf_file_path, 'r', encoding='utf-8') as f:
                        pdf_content = json.load(f)
                        filtered_content = pdf_content.get("filtered_content", "")
                        if filtered_content and filtered_content.strip():
                            pdf_data.append(filtered_content)
                except Exception as e:
                    logger.warning(f"Failed to load PDF data from {pdf_file_path}: {e}")
        
        return pdf_data
    
    def process_multiple_datasets(
        self, 
        base_path: str, 
        output_dir: str, 
        mode: str = 'full'
    ):
        """
        Process multiple dataset folders
        
        Args:
            base_path: Base directory containing dataset folders
            output_dir: Output directory for results
            mode: Processing mode ('full' or 'adaptive')
        """
        os.makedirs(output_dir, exist_ok=True)
        
        processed_count = 0
        skipped_count = 0
        
        for subfolder in os.listdir(base_path):
            if subfolder in ["done.txt", "api_usage_stats.json"]:
                continue
            
            subfolder_path = os.path.join(base_path, subfolder)
            if not os.path.isdir(subfolder_path):
                continue
            
            output_file = os.path.join(output_dir, f"{subfolder}.json")
            
            if self.process_single_dataset(subfolder_path, output_file, mode):
                processed_count += 1
            else:
                skipped_count += 1
        
        logger.info(f"Processing complete. Processed: {processed_count}, Skipped: {skipped_count}")


def main():
    """Main function to run the dataset processing"""
    
    # Configuration
    BASE_PATH = "/path/to/your/dataset/folders"  # Update this path
    OUTPUT_DIR = "/path/to/your/output/directory"  # Update this path
    QUESTION_TYPES_CONFIG = "/path/to/question_type.json"  # Update this path
    PROCESSING_MODE = "adaptive"  # or "full"
    
    try:
        # Initialize processor
        processor = DatasetProcessor(QUESTION_TYPES_CONFIG)
        
        # Process datasets
        processor.process_multiple_datasets(BASE_PATH, OUTPUT_DIR, PROCESSING_MODE)
        
        logger.info("Dataset processing completed successfully!")
        
    except Exception as e:
        logger.error(f"Main execution failed: {e}")
        raise


if __name__ == "__main__":
    main()