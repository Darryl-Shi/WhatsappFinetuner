import openai
import os
import json
import argparse
import time

openai.api_key = os.getenv("OPENAI_API_KEY")

parser = argparse.ArgumentParser(description='Process your whatsapp chat data.')
parser.add_argument('--path', type=str, help='Path to file')
parser.add_argument('--epoch', type=int, help='Number of epochs')
parser.add_argument('--model', type=str, help='Model name')
parser.add_argument('--id', type=str, help='File ID', default='')

args = parser.parse_args()

path = args.path
epoch = args.epoch
model = args.model
id = args.id

if id != '':
    openai.FineTuningJob.create(training_file=id, model=model, hyperparameters={"n_epochs": epoch})
else:
    training_data = openai.File.create(
      file=open(path, "rb"),
      purpose='fine-tune'
    )
    print("Training data uploaded. Waiting 5 minutes before starting training to allow files to process.")
    time.sleep(300)
    openai.FineTuningJob.create(training_file=training_data["id"], model=model, hyperparameters={"n_epochs": epoch})
    
print(openai.FineTuningJob.list(limit=10))
