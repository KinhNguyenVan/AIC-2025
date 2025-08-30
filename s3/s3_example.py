import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from s3_utils import get_public_url, upload_file, upload_many, upload_folder, get_list, download_file, delete_file, get_presigned_url, get_neighbor_frames

# Public URL example
#print(get_public_url("test_upload/JUSTIPH.png"))



# Upload one file
# upload_file("static/images/phan tai.jpg", "test_upload/phan tai.jpg")



# Upload many files
# Upload with explicit object names
# files = [
#     ("static/images/kyyeu.jpg", "test_upload/kyyeu.jpg"),
#     ("static/images/tran thanh.jpg", "test_upload/tran thanh.jpg"),
# ]
# urls = upload_many(files, storage_class="STANDARD", max_workers=10)
# print("Uploaded URLs:", urls)



# Upload entire folder "static/images" into bucket prefix "project_images/"
# urls = upload_folder("static/images", s3_prefix="test_upload_2", max_workers=32)
# print("Uploaded folder URLs:", urls)




# List all files
# get_list(prefix="Keyframes_L30_a")



# Download file
#download_file("cat.jpg", "downloads/cat.jpg")



# Delete file
#delete_file("dog.jpg")



# Get presigned URL (valid 10 mins)
#get_presigned_url("JUSTIPH.png", expiry=600)

neighbors = get_neighbor_frames("Keyframes_L30_a/L30_V064/001326.webp", before=3, after=3)
print("Neighbor frames:", neighbors)