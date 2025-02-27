# ScIRGen-Geo Dataset

**ScIRGen-Geo Dataset**is a large-scale, task-oriented dataset designed for retrieval-augmented generation (RAG) in scientific research, with a focus on the geoscience domain. It is introduced in the paper*ScIRGen: Synthesize Realistic and Large-Scale RAG Dataset for Scientific Research*, which has been submitted to the KDD conference. The dataset is crafted to reflect real-world research inquiries, incorporating realistic questions, detailed dataset metadata, and relevant paper excerpts.

## Repository Structure

The repository is organized into four main directories:

- **full/**  

    Contains the complete dataset, including all data entries and supplementary information.
- **train/**  

    The training split used for model training.
- **dev/**  

    The development (validation) split for hyperparameter tuning and model evaluation.
- **test/**  

    The test split for final evaluation of models.


## How to Use

1. **Clone the Repository:**

    bash

    复制

    `gitclonehttps://github.com/your_username/ScIRGen-Geo.gitcdScIRGen-Geo`
2. **Select the Appropriate Data Split:**  

    Use the`train/`,`dev/`, and`test/`directories based on your experimental needs.
3. **Data Loading and Preprocessing:**  

    Develop data loading scripts (e.g., in Python) to parse and preprocess the dataset according to the provided format.
4. **Experiment Reproduction:**  

    For details on experimental settings and evaluation metrics, please refer to the paper. This will help ensure consistency when reproducing results.

## Citation

If you use this dataset in your research, please cite our paper as follows:

mathematica

复制

`@inproceedings{lin2025scirgen,title={ScIRGen:SynthesizeRealisticandLarge-ScaleRAGDatasetforScientificResearch},author={JunyongLinandLuDaiandRuiqianHanandYijieSuiandRuilinWangandXingliangSunandQinglinWuandMinFengandHaoLiuandHuiXiong},year={2025}}`

## License


## Acknowledgements

We appreciate the contributions and support from the research community in developing the ScIRGen-Geo dataset. For further details and background information, please consult the paper and related publications.

If you have any questions or suggestions, feel free to open an issue in the repository.
