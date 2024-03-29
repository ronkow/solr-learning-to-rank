# solr-learning-to-rank

This is my Master of Science in Artificial Intelligence project.

Please read the project report for details:  
https://github.com/ronkow/solr-learning-to-rank/blob/main/project_report/project_report.pdf

This repository contains the data, models and code for:
- creating datasets (training, validation, testing) for LambdaMART baseline and final models (feature value extraction by Solr)
- converting LambdaMART models to JSON
- uploading feature data, feature definitions (for feature store), and models to Solr
- sending queries to Solr (to compare results by default BM25 ranking and ranking models)
- grammar website (quizzes and search system only)
- setup of search system (database search and Solr search)

This project was developed with invaluable help from https://github.com/sujitpal/ltr-examples
