import openai
import os
import json
import argparse
import time

parser = argparse.ArgumentParser(description='Process your whatsapp chat data.')
parser.add_argument('--path', type=str, help='Path to file')
parser.add_argument('--epoch', type=int, help='Number of epochs')
parser.add_argument('--model', type=str, help='Model name')

args = parser.parse_args()

path = args.path
epoch = args.epoch
model = args.model

openai.api_key = os.getenv("OPENAI_API_KEY")

training_data = openai.File.create(
  file=open(path, "rb"),
  purpose='fine-tune'
)
openai.FineTuningJob.create(training_file=training_data["id"], model=model, hyperparameters={"n_epochs": epoch})

openai.FineTuningJob.list(limit=10)
