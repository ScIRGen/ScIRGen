# -*- coding: utf-8 -*-
"""
revised Bloom's Taxonomy Question Classifier

This script classifies questions based on their cognitive complexity using the revised Bloom's Taxonomy.
It processes JSON files containing questions and adds cognitive level classifications (C1-C6).

Author: Junyong Lin
Date: 2025-06-12
"""

import os
import json
import requests
from typing import Dict, List, Tuple, Optional, Any


class BloomsTaxonomyClassifier:
    """
    A classifier that uses AI to categorize questions according to Bloom's Taxonomy levels.
    """
    
    def __init__(self, api_key: str = "", api_url: str = "https://gpt-api.hkust-gz.edu.cn/v1/chat/completions"):
        """
        Initialize the classifier with API credentials and endpoint.
        
        Args:
            api_key: OpenAI API key for authentication
            api_url: API endpoint URL
        """
        self.api_key = api_key
        self.api_url = api_url
        self.headers = {
            'Content-Type': 'application/json',
            "Authorization": f"Bearer {api_key}"
        }
    
    def send_request(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send a request to the AI API for question classification.
        
        Args:
            data: Request payload containing the prompt and model parameters
            
        Returns:
            API response as dictionary, or None if request fails
        """
        try:
            response = requests.post(self.api_url, headers=self.headers, data=json.dumps(data))
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None
    
    def construct_classification_prompt(self, question: str) -> Dict[str, Any]:
        """
        Construct the prompt for Bloom's Taxonomy classification.
        
        Args:
            question: The question to be classified
            
        Returns:
            Dictionary containing the API request payload
        """
        user_content = f"""**Role:** You are an expert evaluator and cognitive scientist specializing in revised Bloom's Taxonomy.

**Task:** Classify the following question based on its cognitive complexity into one of the six categories (C1–C6) from the revised Bloom's Taxonomy.

### **CATEGORIES AND DESCRIPTIONS:**

**C1 (Remembering):**
- Retrieve relevant knowledge from long-term memory.
- Focus on recalling or recognizing facts, definitions, or basic concepts.
- **Examples:** RECOGNIZING (identifying), RECALLING (retrieving).

**C2 (Understanding):**
- Construct meaning from information through interpretation, explanation, or comparison.
- Emphasis is on understanding concepts rather than simply recalling them.
- **Examples:** INTERPRETING, EXEMPLIFYING, CLASSIFYING, SUMMARIZING, INFERRING, COMPARING, EXPLAINING.

**C3 (Applying):**
- Use knowledge in a new context or apply learned procedures to solve problems.
- Emphasis is on performing tasks or carrying out processes.
- **Examples:** EXECUTING (carrying out), IMPLEMENTING (using).

**C4 (Analyzing):**
- Break down information into parts to understand relationships, patterns, or structures.
- Focus on examining and organizing components.
- **Examples:** DIFFERENTIATING, ORGANIZING, ATTRIBUTING.

**C5 (Evaluating):**
- Make judgments based on criteria, standards, or evidence.
- Focus on assessing or critiquing based on logical reasoning.
- **Examples:** CHECKING, CRITIQUING.

**C6 (Creating):**
- Generate new ideas, designs, or constructs by combining elements in novel ways.
- Focus on producing original work or reassembling existing components into new patterns.
- **Examples:** GENERATING, PLANNING, PRODUCING.

## **Classification Instructions**
1. **Identify the Key Action:** Examine the main verb(s) or action(s) in the question.
2. **Match to Category:** Decide which of the six categories (C1–C6) the question's primary cognitive demand aligns with.
3. **Tie-Breaking Rule:** If the question seems to fit multiple categories, select the one that best represents the dominant cognitive skill required.
4. **Focus on Cognitive Process:** Base your classification on the mental operation needed, not the topic itself.
5. **Output Format:** Provide **only** the category code and name in parentheses (e.g., `C1(Remembering)`, `C2(Understanding)`).

**Question to Classify:** {question}"""

        return {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": user_content}],
            "temperature": 0.1
        }
    
    def classify_questions_in_data(self, data_json: Dict[str, Any]) -> Tuple[Dict[str, int], List[str], Dict[str, Any]]:
        """
        Process all questions in the JSON data and classify them using Bloom's Taxonomy.
        
        Args:
            data_json: JSON data containing questions in the new structure
            
        Returns:
            Tuple containing:
            - API usage statistics
            - List of classification results
            - Updated JSON data with classifications
        """
        api_cost = {'completion_tokens': 0, 'prompt_tokens': 0, 'total_tokens': 0, "consume": 0}
        results = []
        
        # Updated to handle new query structure: {"Disjunctive": [], "Concept Completion": [], ...}
        query_data = data_json.get("query", {})
        
        if not isinstance(query_data, dict):
            raise ValueError("Query data should be a dictionary with category names as keys")
        
        for category_name, questions_list in query_data.items():
            print(f"Processing category: {category_name}")
            
            for question_item in questions_list:
                if not isinstance(question_item, dict) or 'Question' not in question_item:
                    print(f"Skipping invalid question item: {question_item}")
                    continue
                
                question_text = question_item['Question']
                print(f"Classifying: {question_text[:100]}...")
                
                # Send classification request
                response = self.send_request(self.construct_classification_prompt(question_text))
                
                if response is None:
                    print(f"Failed to classify question: {question_text[:50]}...")
                    continue
                
                # Update API cost tracking
                usage = response.get('usage', {})
                api_cost["consume"] += response.get('consume', 0)
                api_cost["total_tokens"] += usage.get("total_tokens", 0)
                api_cost["completion_tokens"] += usage.get("completion_tokens", 0)
                api_cost["prompt_tokens"] += usage.get("prompt_tokens", 0)
                
                # Extract classification result
                classification_result = response['choices'][0].get('message', {}).get('content', '').strip()
                
                if classification_result:
                    question_item['Level'] = classification_result
                    results.append(classification_result)
                    print(f"Classification: {classification_result}")
        
        print(f"API Usage Summary: {api_cost}")
        return api_cost, results, data_json
    
    def save_json(self, data: Dict[str, Any], filepath: str) -> None:
        """
        Save data to JSON file with proper encoding.
        
        Args:
            data: Data to be saved
            filepath: Output file path
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)


def process_json_files(input_directory: str, output_directory: str, api_key: str) -> None:
    """
    Process all JSON files in a directory and classify questions using revised Bloom's Taxonomy.
    
    Args:
        input_directory: Directory containing input JSON files
        output_directory: Directory to save processed files
        api_key: API key for the classification service
    """
    classifier = BloomsTaxonomyClassifier(api_key=api_key)
    processed_count = 0
    
    # Ensure output directory exists
    os.makedirs(output_directory, exist_ok=True)
    
    for filename in os.listdir(input_directory):
        if not filename.endswith('.json'):
            continue
            
        file_path = os.path.join(input_directory, filename)
        
        try:
            # Load JSON data
            with open(file_path, 'r', encoding='utf-8') as f:
                data_json = json.load(f)
            
            # Skip if already processed
            if "bloom_taxonomy_cost" in data_json:
                processed_count += 1
                print(f"{filename} already processed, skipping...")
                continue
            
            print(f"Processing {filename}...")
            
            # Classify questions
            api_usage, results, updated_json = classifier.classify_questions_in_data(data_json)
            
            # Add processing metadata
            updated_json["bloom_taxonomy_cost"] = api_usage
            updated_json["processing_metadata"] = {
                "total_classifications": len(results),
                "processed_file": filename
            }
            
            # Save results
            file_id = updated_json.get("id", filename.replace('.json', ''))
            output_path = os.path.join(output_directory, f"{file_id}.json")
            classifier.save_json(updated_json, output_path)
            
            processed_count += 1
            print(f"Successfully processed {filename}. Total processed: {processed_count}")
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            continue


def main():
    """
    Main function to run the Bloom's Taxonomy classification process.
    
    Configuration:
    - Update the paths and API key before running
    - Ensure input directory contains JSON files with the correct structure
    """
    # Configuration - Update these paths and API key
    INPUT_DIR = "/path/to/your/input/directory"
    OUTPUT_DIR = "/path/to/your/output/directory" 
    API_KEY = "your-api-key-here"  # Add your actual API key
    
    # Validate configuration
    if not os.path.exists(INPUT_DIR):
        print(f"Input directory does not exist: {INPUT_DIR}")
        return
    
    if not API_KEY or API_KEY == "your-api-key-here":
        print("Please configure your API key in the main() function")
        return
    
    print("Starting revised Bloom's Taxonomy Question Classification...")
    print(f"Input Directory: {INPUT_DIR}")
    print(f"Output Directory: {OUTPUT_DIR}")
    
    process_json_files(INPUT_DIR, OUTPUT_DIR, API_KEY)
    print("Processing complete!")


if __name__ == "__main__":
    main()