import cloudinary
import cloudinary.uploader
import requests

def upload_file_to_cloudinary(file_path):
    cloudinary.config(
        cloud_name="dsk0rkidm",
        api_key="144961215391363",
        api_secret="c3Ww9NrAQi5E3C0BmWU2xIZ6Nj0"
    )

    try:
        # Upload file to Cloudinary
        response = cloudinary.uploader.upload(file_path, resource_type="auto")

        # Return the URL of the uploaded file
        return response['url']
    except Exception as e:
        return f"Error uploading file: {e}"

def upload_file_to_fileio(image_path):
    url = "https://file.io"  # Correct URL for File.io upload
    try:
        with open(image_path, 'rb') as file:
            response = requests.post(url, files={"file": file})
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print("Image uploaded successfully:", result["link"])
                    return result["link"]
                else:
                    print("Upload failed:", result.get("message"))
            else:
                print("HTTP Error:", response.status_code)
    except Exception as e:
        print("Error:", e)
        return None

