import os
import requests
from tqdm import tqdm

class CloudFrontManager:
    def __init__(self, distribution_domain, s3_manager=None):
        """
        distribution_domain: your CloudFront domain (e.g. dxxxxx.cloudfront.net)
        s3_manager: optional S3Manager instance to list files
        """
        self.domain = distribution_domain
        self.s3_manager = s3_manager

    def public_url(self, object_key):
        """
        Return the CloudFront URL for a given object.
        """
        return f"https://{self.domain}/{object_key}"

    def list_files(self, prefix=""):
        """
        List files via S3Manager, but return CloudFront URLs.
        """
        if not self.s3_manager:
            raise ValueError("S3Manager is required for listing files")
        keys = self.s3_manager.list_files(prefix=prefix)
        return [self.public_url(k) for k in keys]

    def download_file(self, object_key, dest_path):
        """
        Download a single file from CloudFront.
        """
        url = self.public_url(object_key)
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total = int(response.headers.get("content-length", 0))
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        with open(dest_path, "wb") as f, tqdm(
            total=total, unit="B", unit_scale=True, desc=f"Downloading {os.path.basename(dest_path)}"
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))

        print(f"✅ Downloaded {url} → {dest_path}")

    def download_folder(self, prefix, dest_folder):
        """
        Download all files under a prefix via CloudFront.
        """
        if not self.s3_manager:
            raise ValueError("S3Manager is required for folder download")

        keys = self.s3_manager.list_files(prefix=prefix)
        if not keys:
            print(f"📂 No files found under prefix {prefix}")
            return

        for key in keys:
            relative_path = key[len(prefix):] if prefix else key
            local_path = os.path.join(dest_folder, relative_path)
            self.download_file(key, local_path)
