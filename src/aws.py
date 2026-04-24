import boto3
import json
from botocore.exceptions import ClientError, BotoCoreError
import io
import pandas as pd
from src.logger import get_logger

logger = get_logger(__name__)

def get_secret(secret_name, region_name="us-east-1"):
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    logger.info("Retrieving secret: %s", secret_name)
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        logger.error("Failed to retrieve secret '%s': %s", secret_name, e)
        raise Exception(f"Failed to retrieve secret '{secret_name}': {e}") from e
    except (BotoCoreError, Exception) as e:
        logger.error("Unexpected error retrieving secret '%s': %s", secret_name, e)
        raise Exception(f"Unexpected error retrieving secret '{secret_name}': {e}") from e

    logger.info("Successfully retrieved secret: %s", secret_name)
    secret = get_secret_value_response['SecretString']
    return json.loads(secret)

def get_s3_file(file, bucket='realitystats'):
    logger.info("Fetching s3://%s/data/%s", bucket, file)
    try:
        session = boto3.session.Session()
        s3 = session.client("s3")
        obj = s3.get_object(Bucket=bucket, Key=f"data/{file}")
        with obj['Body'] as body:
            df = pd.read_csv(io.BytesIO(body.read()))
        logger.info("Successfully fetched s3://%s/data/%s (%d rows)", bucket, file, len(df))
        return df
    except ClientError as e:
        logger.error("Failed to retrieve S3 file '%s' from bucket '%s': %s", file, bucket, e)
        raise Exception(f"Failed to retrieve S3 file '{file}' from bucket '{bucket}': {e}") from e
    except (BotoCoreError, Exception) as e:
        logger.error("Unexpected error retrieving S3 file '%s': %s", file, e)
        raise Exception(f"Unexpected error retrieving S3 file '{file}': {e}") from e
