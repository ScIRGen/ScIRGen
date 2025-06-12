# ScIRGen-Geo Dataset

## Overview

The **ScIRGen-Geo Dataset** is a large-scale, task-oriented dataset designed for retrieval-augmented generation (RAG) in scientific research, with a focus on the geoscience domain. The corpus is fully bilingual (English ↔ Chinese), offering parallel content in both languages. 

This dataset is introduced in the paper **"ScIRGen: Synthesize Realistic and Large-Scale RAG Dataset for Scientific Research"**, which has been accepted by the KDD conference. The dataset is crafted to reflect real-world research inquiries, incorporating realistic questions, detailed dataset metadata, and relevant paper excerpts.

## Dataset Structure

The dataset follows a comprehensive JSON structure with the following components:

```json
{
  "id": "Unique UUID for the data record, used for precise reference",
  "relatedPaper": "Number of related papers",
  "context": {
    "metadata": {
      "titleEn": "English title",
      "titleCn": "Chinese title",
      "description": "English abstract: describes the dataset",
      "descriptionCn": "Chinese abstract",
      "instructions": "English usage instructions",
      "instructionsCn": "Chinese usage instructions",
      "east": "Eastern longitude",
      "west": "Western longitude",
      "south": "Southern latitude",
      "north": "Northern latitude",
      "startTime": "Start of data time range (UTC)",
      "endTime": "End of data time range",
      "fileSize": "Total file size (bytes)",
      "cstr": "Internal accession number",
      "doi": "DOI",
      "dataFormat": "Data format",
      "license": "License identifier"
    },
    "authorList": "Array of author information",
    "literatureList": "Array of literature references",
    "keywordStandList": "Array of standard keywords",
    "themeList": "Array of theme information",
    "placeKeywordList": "Array of place keywords",
    "temporalKeywordList": "Array of temporal keywords",
    "fundVOList": "Array of funding project information",
    "projectList": "Array of data platform information",
    "relatedDataList": "Array of related dataset information"
  },
  "extract_pdfs_data": [
    {
      "background": ["", "…"],
      "research objective": ["", "…"],
      "challenges": ["", "…"],
      "methods": ["", "…"],
      "dataset": ["", "…"],
      "findings": ["", "…"],
      // Chinese version
      "backgroundCn": ["", "…"],
      "research objectiveCn": ["", "…"],
      "challengesCn": ["", "…"],
      "methodsCn": ["", "…"],
      "datasetCn": ["", "…"],
      "findingsCn": ["", "…"]
    }
  ],
  "query": {
    "Verification": [
      {
        "QuestionEn": "Sample verification question (English)",
        "QuestionCn": "Sample verification question (Chinese)",
        "AnswerEn": "Sample answer (English)",
        "AnswerCn": "Sample answer (Chinese)",
        "Level": "C5(Evaluating)"
      }
    ],
    "Interpretation": [
      {
        "QuestionEn": "What methodological strategies can be employed to minimize errors in long-term vegetation mapping using remote sensing data?",
        "QuestionCn": "在使用遥感数据进行长期植被制图时，可以采用哪些方法论策略来最小化错误？",
        "AnswerEn": "Methodological strategies such as selecting stable samples and features for mapping and applying spatial filtering can be employed to minimize errors in long-term vegetation mapping using remote sensing data, as these approaches help ensure consistency and improve accuracy across different time periods.",
        "AnswerCn": "可以采用选择稳定样本和特征进行制图以及应用空间滤波等方法策略，以最小化使用遥感数据进行长期植被制图中的错误，因为这些方法有助于确保一致性并提高不同时间段的准确性。",
        "Level": "C6(Creating)"
      }
    ]
  }
}
```

## Repository Structure

The repository is organized into four main directories:

- **`full/`**: Contains the complete dataset, including all data entries and supplementary information
- **`train/`**: The training split used for model training
- **`dev/`**: The development (validation) split for hyperparameter tuning and model evaluation
- **`test/`**: The test split for the final evaluation of models

## How to Use

### 1. Clone the Repository

```bash
git clone https://github.com/your_username/ScIRGen-Geo.git
cd ScIRGen-Geo
```

### 2. Select the Appropriate Data Split

Use the `train/`, `dev/`, and `test/` directories based on your experimental needs.

### 3. Data Loading and Preprocessing

Develop data loading scripts (e.g., in Python) to parse and preprocess the dataset according to the provided format.

### 4. Experiment Reproduction

For details on experimental settings and evaluation metrics, please refer to the paper. This will help ensure consistency when reproducing results.

## Citation

If you use the ScIRGen-Geo dataset in your research, please cite our paper as follows:

```bibtex
@inproceedings{
  lin2025scirgen,
  title={ScIRGen: Synthesize Realistic and Large-Scale RAG Dataset for Scientific Research},
  author={Junyong Lin and Lu Dai and Ruiqian Han and Yijie Sui and Ruilin Wang and Xingliang Sun and Qinglin Wu and Min Feng and Hao Liu and Hui Xiong},
  year={2025}
}
```

**Full Citation:**
Junyong Lin, Lu Dai, Ruiqian Han, Yijie Sui, Ruilin Wang, Xingliang Sun, Qinglin Wu, Min Feng, Hao Liu, and Hui Xiong. 2025. ScIRGen: Synthesize Realistic and Large-Scale RAG Dataset for Scientific Research. In Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25), August 3–7, 2025, Toronto, ON, Canada. ACM, New York, NY, USA, 17 pages. https://doi.org/10.1145/3711896.3737432

## Acknowledgements

We appreciate the contributions and support from the research community in developing the ScIRGen-Geo dataset. For further details and background information, please consult the paper and related publications. 

If you have any questions or suggestions, feel free to open an issue in the repository.
