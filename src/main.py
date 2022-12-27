import kfp
import kfp.compiler as compiler
import json
import string
import random
import logging
import sys
import os

# Setting logging level
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# Set vars
host = os.getenv("KUBEFLOW_URL")
client_id = os.getenv("CLIENT_ID")
other_client_id = os.getenv("OTHER_CLIENT_ID")
other_client_secret = os.getenv("OTHER_CLIENT_SECRET")
pipeline_path = os.getenv("PIPELINE_FILE_PATH")
pipeline_id = os.getenv("PIPELINE_ID")
pipeline_name = os.getenv("PIPELINE_NAME")
experiment_id = os.getenv("EXPERIMENT_ID")
namespace = os.getenv("NAMESPACE")
run_pipeline = os.getenv("RUN_PIPELINE")

# Random value used for naming
def random_suffix() -> string:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))

run_name = 'run-' + str(pipeline_name) + "-" + random_suffix()

# Authenticate session client
client = kfp.Client(host=host, 
    client_id=client_id, 
    other_client_id=other_client_id, 
    other_client_secret=other_client_secret,
    namespace=namespace
)

# Get new version name
version_obj = client.pipelines.list_pipeline_versions(
    resource_key_id=pipeline_id
)
version_count = version_obj.total_size
version = int(version_count) + 1

# Upload pipeline into new version
client.pipeline_uploads.upload_pipeline_version(
    pipeline_path,
    name=version,
    pipelineid=pipeline_id
)

# Run uploaded pipeline
client.run_pipeline(
    pipeline_id=pipeline_id,
    experiment_id=experiment_id,
    job_name=run_name
)
logging.info(f"A run is created with: {job_name}")
