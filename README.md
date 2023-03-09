# Kubeflow Pipelines Deploy Action

GitHub Actions for compiling and deploying pipelines on GCP/GKE's Kubeflow instances.

The action creates a new pipeline if the pipeline doesn't exist in Kubeflow. If it exists, it will create a new version.

## Workflow Configuration
### Parameters

The action has been set up with only two input parameters:

| key                       | required | description                                                                                                                  | 
| :------------------------ | -------- | ---------------------------------------------------------------------------------------------------------------------------- | 
| PIPELINE_FILE_PATH        | True     | The full path to pipeline.py file. This must be relative to the root of the GitHub repository where the Action is triggered. |
| PIPELINE_DESCRIPTION      | False    | Optional description of the pipeline. Can be used to override default value for instance for testing branches.               |
| PIPELINE_NAME_STRING      | False    | Optional string value to attach to the pipeline name. Can be used for testing purposes.                                      |

Default pipeline name will be the same as the filename of the pipeline. IMPORTANT: Pipeline function should also have the same name.



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

#### Define Workflow for single pipeline

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

```

#### Define Workflow to run for all changed pipelines in a the `pipelines` folder

The following workflow will make a list of any new or modified pipeline inside a specific folder, and deploy each of them.
```yaml
name: Compile, Deploy and Run on Kubeflow
on:
  push:
    branches:
      - main
    paths:
      - 'pipelines/**'

jobs:
  changed-files:
    name: Get changed pipelines
    runs-on: ubuntu-latest

    outputs:
      matrix: ${{ steps.set-matrix.outputs.matrix }}

    steps:
    - name: Checkout files in repo
      uses: actions/checkout@v3
      with:
          fetch-depth: 0

    - name: Get changed files in the pipelines folder
      id: changed-files
      uses: tj-actions/changed-files@v35.2.0
      with:
        json: true
        files: |
          pipelines/**

    - name: List all changed files
      run: echo '${{ steps.changed-files.outputs.all_changed_files }}'

    - id: set-matrix
      run: echo "matrix={\"container\":${{ steps.changed-files.outputs.all_changed_files }}}" >> "$GITHUB_OUTPUT"

  deploy-pipelines:
    name: Deploy changed pipelines
    runs-on: ubuntu-latest
    needs: [changed-files]

    strategy:
      matrix: ${{ fromJSON(needs.changed-files.outputs.matrix) }}
      max-parallel: 4
      fail-fast: false

    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Submit a pipeline
        uses: albert-cintas-pot/kubeflow-compile-deploy@v0.2.2
        env:
          KUBEFLOW_URL: ${{ secrets.KUBEFLOW_URL }}
          KFP_CREDENTIALS_JSON: ${{ secrets.KFP_CREDENTIALS_JSON }}
          CLIENT_ID: ${{ secrets.CLIENT_ID }}
          OTHER_CLIENT_ID: ${{ secrets.OTHER_CLIENT_ID }}
          OTHER_CLIENT_SECRET: ${{ secrets.OTHER_CLIENT_SECRET }}
          PIPELINE_FILE_PATH: ${{ matrix.container }}


```

### Docker image creation

A github action has been setup in this repository to create a Docker image with KFP SDK installed for use in this action. This shaves 30 seconds of time each time a Kubeflop pipeline is deployed, helping in pipeline testing.
