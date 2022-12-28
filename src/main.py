import kfp
import kfp.compiler as compiler
import string
import random
import logging
import sys
import os
import importlib.util

# Setting logging level
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# Set vars
host = os.getenv("KUBEFLOW_URL")
client_id = os.getenv("CLIENT_ID")
other_client_id = os.getenv("OTHER_CLIENT_ID")
other_client_secret = os.getenv("OTHER_CLIENT_SECRET")
pipeline_path = os.getenv("PIPELINE_FILE_PATH")
pipeline_func_name = os.getenv("PIPELINE_FUNC_NAME")
pipeline_id = os.getenv("PIPELINE_ID")
pipeline_name = os.getenv("PIPELINE_NAME")
experiment_name = os.getenv("EXPERIMENT_NAME")
namespace = os.getenv("NAMESPACE")
run_pipeline = os.getenv("RUN_PIPELINE")

# S
if not pipeline_name:
    pipeline_name = pipeline_func_name

# Random value used for naming
def random_suffix() -> string:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    
run_name = 'run-' + str(pipeline_name) + "-" + random_suffix()

# Authenticate session client
client = kfp.Client(host=host, 
    client_id=client_id, 
    other_client_id=other_client_id, 
    other_client_secret=other_client_secret,
    namespace=str(namespace)
)

# Compile pipeline
def load_pipeline_from_path(
    pipeline_func_name: str, pipeline_path: str
) -> staticmethod:
    spec = importlib.util.spec_from_file_location(
        pipeline_func_name, pipeline_path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, pipeline_func_name)

pipeline_function = load_pipeline_from_path(
        pipeline_func_name=pipeline_func_name,
        pipeline_path=pipeline_path,
    )

zip_name = pipeline_function.__name__ + ".zip"
compiler.Compiler().compile(pipeline_function, zip_name)

# Get new version name
version_obj = client.pipelines.list_pipeline_versions(
    resource_key_id=str(pipeline_id)
)
version_count = version_obj.total_size
version = int(version_count) + 1

# Upload pipeline into new version
client.pipeline_uploads.upload_pipeline_version(
    zip_name,
    name=version,
    pipelineid=pipeline_id
)

# Get experiment_id from experiment_name
experiment_id = client.get_experiment(
    experiment_name=experiment_name
).id

# Run uploaded pipeline
if run_pipeline == "True":
    client.run_pipeline(
        pipeline_id=pipeline_id,
        experiment_id=experiment_id,
        job_name=run_name
        )
    logging.info(f"A run is created with: {run_name}")
else:
    logging.info(f"Version {version} has been created for pipeline: {pipeline_name}")
