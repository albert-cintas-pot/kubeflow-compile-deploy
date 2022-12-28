# Kubeflow Pipelines Deploy Action

GitHub Actions for compiling, deploying and running pipelines on GCP/GKE's full Kubeflow deploys. 

## Workflow Configuration
### Parameters

| key                       | required | description                                                                                                                  | 
| :------------------------ | -------- | ---------------------------------------------------------------------------------------------------------------------------- | 
| PIPELINE_FILE_PATH        | True     | The full path to pipeline.py file. This must be relative to the root of the GitHub repository where the Action is triggered. | 
| PIPELINE_FUNC_NAME        | True     | The name of the pipeline function. This name will be the name of the pipeline if the name is empty.                          | 
| PIPELINE_ID               | True     | The ID of the pipeline. You can get it from the Kubeflow dashboard.                                                          |
| PIPELINE_NAME             | False    | The name of the pipeline.                                                                                                    | 
| NAMESPACE                 | True     | The namespace in which the pipeline should run.                                                                              | 
| EXPERIMENT_NAME           | True     | The name of the experiment name within which the kubeflow pipeline should run.                                               | 
| RUN_PIPELINE              | False    | The flag of running the pipeline. Defaults to False.                                                                         | 

### Authentication secrets and parameters

We use the Kubeflow SDK to authenticate to the Kubeflow instance as stated in the official docs: https://www.kubeflow.org/docs/distributions/gke/pipelines/authentication-sdk/#connecting-to-kubeflow-pipelines-in-a-full-kubeflow-deployment

Note that OTHER_CLIENT_ID credentials should be initialized locally before using them in the action, to get the KFP credentials JSON.

The following secrets are mandatory for proper auth:

| key                       | description                                                                                                                                                                      | 
| :------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | 
| KUBEFLOW_URL              | The url endpoint where your Kubeflow UI is running.                                                                                                                              | 
| CLIENT_ID                 | The client ID used by Identity-Aware Proxy at the time of deploying Kubeflow.                                                                                                    | 
| OTHER_CLIENT_ID           | The client ID used to obtain the auth codes and refresh tokens (https://cloud.google.com/iap/docs/authentication-howto#authenticating_from_a_desktop_app).                       | 
| OTHER_CLIENT_SECRET       | The client secret used to obtain the auth codes and refresh tokens.                                                                                                              |
| KFP_CREDENTIALS_JSON      | The JSON file containing the credentials generated the first time you init the SDK client using above credentials (stored at: $HOME/.config/kfp/credentials.json.                |

### Usage

#### Define Workflow for Run after deploy

```yaml
name: Compile, Deploy and Run on Kubeflow
on: [push]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout files in repo
      uses: actions/checkout@v2

    - name: Submit a pipeline
      uses: albert-cintas-pot/kubeflow-compile-deploy-run@main
      env:
        KUBEFLOW_URL: ${{ secrets.KUBEFLOW_URL }} # Required for AUTH
        KFP_CREDENTIALS_JSON: ${{ secrets.KFP_CREDENTIALS_JSON }} # Required for AUTH
        CLIENT_ID: ${{ secrets.CLIENT_ID }} # Required for AUTH
        OTHER_CLIENT_ID: ${{ secrets.OTHER_CLIENT_ID }} # Required for AUTH
        OTHER_CLIENT_SECRET: ${{ secrets.OTHER_CLIENT_SECRET }} # Required for AUTH
        PIPELINE_FILE_PATH: "pipeline.py" # Required
        PIPELINE_FUNC_NAME: "sample_pipeline" # Required 
        PIPELINE_ID: "b47bfa1c-6983-4c23-9979-9a912f39e934" # Required
        PIPELINE_NAME: "coin-flip"
        EXPERIMENT_NAME: "Test Experiment" # Required
        NAMESPACE: "albert-cintas"
        RUN_PIPELINE: "True" # Defaults to False

```
