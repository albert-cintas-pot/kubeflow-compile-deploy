import kfp
import kfp.compiler as compiler
import logging
import sys
import os
import importlib.util
import json

# Setting logging level
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# Set vars
host = os.getenv("KUBEFLOW_URL")
client_id = os.getenv("CLIENT_ID")
other_client_id = os.getenv("OTHER_CLIENT_ID")
other_client_secret = os.getenv("OTHER_CLIENT_SECRET")
pipeline_path = os.getenv("PIPELINE_FILE_PATH")
pipeline_description = os.getenv("PIPELINE_DESCRIPTION")
pipeline_name_string = os.getenv("PIPELINE_NAME_STRING")

# Authenticate session client
client = kfp.Client(host=host, 
    client_id=client_id, 
    other_client_id=other_client_id, 
    other_client_secret=other_client_secret
)

# Set pipeline and function names
pipeline_func_name = pipeline_path.split('/')[-1].rsplit('.', 1)[0]

if pipeline_name_string is not None:
    pipeline_name = pipeline_func_name + '-' + pipeline_name_string
else:
    pipeline_name = pipeline_func_name

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

# Add a filter for the list_pipelines method
filter = json.dumps({'predicates': [{'key': 'name', 'op': 1, 'string_value': '{}'.format(pipeline_name)}]})
filter_pipeline = client.pipelines.list_pipelines(filter=filter)

try:
    does_exist = filter_pipeline.pipelines[0]
    pipeline_exists = True
except TypeError:
    pipeline_exists = False

if pipeline_exists:
    pipeline_id = client.get_pipeline_id(pipeline_name)

    # Get new version name
    version_obj = client.pipelines.list_pipeline_versions(
        resource_key_id=str(pipeline_id)
    )
    version_count = version_obj.total_size
    version = int(version_count) + 1

    

    # Upload pipeline into new version
    if pipeline_description is not None:
        client.pipeline_uploads.upload_pipeline_version(
            zip_name,
            name=version,
            pipelineid=pipeline_id,
            description=pipeline_description
        )
    else:
        client.pipeline_uploads.upload_pipeline_version(
            zip_name,
            name=version,
            pipelineid=pipeline_id
        )

    logging.info(f"Version {version} has been created for pipeline: {pipeline_name}")

# If the pipeline does not exist, upload new one
else:
    if pipeline_description is not None:
        client.pipeline_uploads.upload_pipeline(
            zip_name,
            name=pipeline_name,
            description=pipeline_description
        )
    else:
        client.pipeline_uploads.upload_pipeline(
            zip_name,
            name=pipeline_name
        )
        
    logging.info(f"New pipeline '{pipeline_name}'  has been deployed")
