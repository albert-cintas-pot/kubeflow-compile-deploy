#!/bin/bash

# Set up Kubeflow credentials
echo "${KFP_CREDENTIALS_JSON}" > ~/.config/kfp/credentials.json

python /app/src/main.py
