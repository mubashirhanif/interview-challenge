# How to deploy
Using AWS SAM
1. sam build -t template.yaml
2. sam deploy

# Notes
This version uses 
1. PyTesseract
2. AWS Textract

# Notes
It took me around 1.5 hours to complete this assignment, Majority of which was getting PyTesseract to work on AWS Lambda.
For it to work I had to use the prebuilt binaries from "https://github.com/bweigel/aws-lambda-tesseract-layer", and bake it as an additional lambda layer.
