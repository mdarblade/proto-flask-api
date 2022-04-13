import json
from loguru import logger
import subprocess
import time

REPO_NAME = "marketingmanager"
MODEL_VERSION = "001"
API_NAME = "marketingmanager-api"
DATA_CAPTURE_S3_BUCKET = ""


ACCOUNT_ID = "702773546451"
REGION = "us-west-2"
TAG_NAME = "latest"
ARN_ROLE = "arn:aws:iam::702773546451:role/SageMakerFullAccessRole"
VPC_CONFIG = "SecurityGroupIds=sg-0f6d65feb640b25ce,Subnets=subnet-0106e5dc4e8348710,subnet-0b9c5b64ad01e0eeb"
API_ROLE = "arn:aws:iam::702773546451:role/APIGatewayAccessToSageMaker"
ENDPOINT_NAME = f"{REPO_NAME}-{MODEL_VERSION}"


URI = f"{ACCOUNT_ID}.dkr.ecr.{REGION}.amazonaws.com/{REPO_NAME}"
SAGEMAKER_ARN = (
    f"arn:aws:sagemaker:{REGION}:{ACCOUNT_ID}\:endpoint-config/{ENDPOINT_NAME}"
)
CONFIG_NAME = f"{ENDPOINT_NAME}-config"


def command(string, is_json_output=True):
    """
    Run the string command and return the ouptut

    Args:
        string (str): The command to run

    Returns:
        str: The ouptut of the command
    """
    # string = string.replace("\n", " ")
    print(repr(string))

    if string[:3] == "aws":
        if not is_json_output:
            return subprocess.check_output(string, stderr=subprocess.STDOUT, shell=True)
        string += " --output json"
        message = subprocess.check_output(string, stderr=subprocess.STDOUT, shell=True)
        if message:
            return json.loads(message)
        else:
            return None

    return subprocess.check_output(string, stderr=subprocess.STDOUT, shell=True)


def create_ecr_image():
    """
    Create an ecr image and return the URI.
    """
    logger.info("Create an ecr image and return the URI.")

    # command(f"sudo docker build -f Dockerfile -t {REPO_NAME} .")

    command(
        "aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 702773546451.dkr.ecr.us-west-2.amazonaws.com",
        is_json_output=False,
    )

    result = command("aws ecr describe-repositories")

    try:
        command(
            f"aws ecr create-repository --region {REGION} --repository-name {REPO_NAME}"
        )
        logger.info("No ecr images, created one")
    except subprocess.CalledProcessError:
        logger.info(f"Ecr images already there, pushing code to it.")

    command(f"docker tag {REPO_NAME} {URI}:{TAG_NAME}")
    command(f"docker push {URI}:{TAG_NAME}")


def create_sagemaker_endpoint():
    """
    Create the sagemaker endpoint.
    """
    logger.info("Create the sagemaker endpoint.")

    try:
        command(
            f"""aws sagemaker create-model \
            --model-name {ENDPOINT_NAME} \
            --primary-container Image={URI} \
            --execution-role-arn {ARN_ROLE} \
            --vpc-config {VPC_CONFIG} \
            --region {REGION}"""
        )

    except subprocess.CalledProcessError:
        try:
            logger.info(f"Model already exists.")
            command(
                f"aws sagemaker  delete-model --model-name {ENDPOINT_NAME}"
                f" --region {REGION}"
            )
            command(
                f"aws sagemaker  delete-endpoint-config --endpoint-config-name "
                f"{CONFIG_NAME} --region {REGION}"
            )
            # command(f"aws sagemaker  stop-endpoint --endpoint-name {ENDPOINT_NAME}")
            command(
                f"aws sagemaker  delete-endpoint --endpoint-name {ENDPOINT_NAME}"
                f" --region {REGION}"
            )
        except:
            pass

        time.sleep(10)

        command(
            f"""aws sagemaker create-model \
            --model-name {ENDPOINT_NAME} \
            --primary-container Image={URI} \
            --execution-role-arn {ARN_ROLE} \
            --vpc-config {VPC_CONFIG} \
            --region {REGION}"""
        )

    variant = (
        f"variant-1,ModelName={ENDPOINT_NAME},InitialInstanceCount=1,"
        "InstanceType=ml.m4.xlarge,InitialVariantWeight=1"
    )

    input_capture = (
        "--data-capture-config EnableCapture=true,InitialSamplingPercentage=100,"
        f"DestinationS3Uri={DATA_CAPTURE_S3_BUCKET},CaptureOptions=["
        '{CaptureMode="Input"},{CaptureMode="Output"}]'
    )

    command(
        f"""aws sagemaker create-endpoint-config \
            --endpoint-config-name {CONFIG_NAME} \
            --production-variants VariantName={variant} \
            --region {REGION}"""
    )

    command(
        f"""aws sagemaker create-endpoint \
        --endpoint-name {ENDPOINT_NAME} \
        --endpoint-config-name {CONFIG_NAME} \
        --region {REGION}"""
    )


def create_api_gateway():
    """
    Create the AWS API GATEWAY endpoint.
    """

    logger.info("Create the AWS API GATEWAY endpoint.")

    rest_apis = command("aws apigateway get-rest-apis ")["items"]

    if API_NAME not in [rest_api["name"] for rest_api in rest_apis]:
        api_id = command(
            f"""aws apigateway create-rest-api \
                --name {API_NAME} \
                --api-version {MODEL_VERSION}"""
        )["id"]

        logger.info(f"Creating API id={api_id}")
    else:
        for rest_api in rest_apis:
            if API_NAME == rest_api["name"]:
                api_id = rest_api["id"]
                logger.info(f"Using existing API id={api_id}")
                break

    resource_id = "d3wawmbjae"
    integration_command = (
        "aws apigateway put-integration "
        f"--rest-api-id {api_id} "
        f"--resource-id {resource_id} "
        "--http-method GET "
        "--type AWS "
        "--integration-http-method POST "
        "--uri arn:aws:apigateway:us-west-2:api.sagemaker:path/endpoint/arv-estimator-test-001-endpoint/invocations "
        "--credentials arn:aws:iam::702773546451:role/APIGatewayAccessToSageMaker "
        "--request-templates file:///Users/mdarblade/code/lh-data-workflow/sagemaker/arv/integration_template.json "
        "--passthrough-behavior NEVER"
    )
    logger.info(integration_command)

    command(integration_command)


def run():
    logger.info(f"Deploying {REPO_NAME}-{MODEL_VERSION} to {API_NAME}")
    create_ecr_image()
    create_sagemaker_endpoint()
    # create_api_gateway()


if __name__ == "__main__":
    run()
