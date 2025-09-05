import os
import time
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter, Retry

class CloudFrontManager:
    def __init__(self, distribution_domain, s3_manager=None, max_workers=10):
        """
        distribution_domain: CloudFront domain (e.g. dxxxxx.cloudfront.net)
        s3_manager: optional S3Manager instance to list files
        max_workers: số lượng luồng tải song song
        """
        self.domain = distribution_domain
        self.s3_manager = s3_manager
        self.max_workers = max_workers

        # Tạo session với retry
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def public_url(self, object_key):
        return f"https://{self.domain}/{object_key}"

    def list_files(self, prefix=""):
        if not self.s3_manager:
            raise ValueError("S3Manager is required for listing files")
        keys = self.s3_manager.list_files(prefix=prefix)
        return keys  # Trả về key gốc (không gắn prefix CloudFront)

    def download_file(self, object_key, dest_path, pbar=None):
        """
        Download a single file with retry logic.
        """
        url = self.public_url(object_key)
        try:
            response = self.session.get(url, stream=True, timeout=15)
            response.raise_for_status()

            total = int(response.headers.get("content-length", 0))
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            with open(dest_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=64 * 1024):  # 64KB chunks
                    if chunk:
                        f.write(chunk)
                        if pbar:
                            pbar.update(len(chunk))

            return True, url
        except requests.exceptions.RequestException as e:
            return False, f"❌ Lỗi tải {url}: {e}"

    def download_folder(self, prefix, dest_folder):
        """
        Download all files under a prefix (parallel + progress).
        Uses S3 ListObjectsV2 sizes to avoid HEAD requests.
        """
        if not self.s3_manager:
            raise ValueError("S3Manager is required for folder download")

        files = self.list_files(prefix)
        if not files:
            print(f"📂 No files found under prefix {prefix}")
            return

        # Tính tổng dung lượng từ S3 list, không cần HEAD
        total_size = sum(f["Size"] for f in files)

        with tqdm(total=total_size, unit="B", unit_scale=True, desc="Downloading folder") as pbar:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = []
                for f in files:
                    key = f["Key"]
                    relative_path = key[len(prefix):] if prefix else key
                    local_path = os.path.join(dest_folder, relative_path)
                    futures.append(executor.submit(self.download_file, key, local_path, pbar))

                for future in as_completed(futures):
                    success, message = future.result()
                    if not success:
                        print(message)

        print("✅ Hoàn tất tải toàn bộ folder!")
