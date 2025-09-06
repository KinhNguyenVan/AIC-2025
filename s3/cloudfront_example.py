import sys
import os

from s3_manager import S3Manager
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cloudfront_manager import CloudFrontManager
from dotenv import load_dotenv
load_dotenv()

# Initialize S3 manager (for listing keys only)
s3 = S3Manager(
    bucket_name="aic-bucket-hcmus",
    region=os.environ.get("AWS_REGION"),
    aws_access_key=os.environ.get("AWS_ACCESS_KEY"),
    aws_secret_key=os.environ.get("AWS_SECRET_KEY")
)
# Initialize CloudFront manager
cf = CloudFrontManager("d1zgby2rss028i.cloudfront.net", s3_manager=s3)




# List files (returns CloudFront URLs instead of S3 URLs)
# urls = cf.list_files(prefix="Keyframes_L28_a/L28_V016/")
# print(urls[:5])  # show first 5 CloudFront URLs

# Download a single file
# cf.download_file("Keyframes_L28_a/L28_V016/028779.webp", "downloads/028779.webp")

# Download a whole folder
cf.download_folder("Keyframes_K07/", "D:/s3Keyframes_K07")

