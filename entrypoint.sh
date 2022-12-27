#!/bin/bash

# Set up Kubeflow credentials
mkdir -p /github/home/.config/kfp/
echo "${KFP_CREDENTIALS_JSON}" > /github/home/.config/kfp/credentials.json

python /app/src/main.py
