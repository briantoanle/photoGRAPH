from flask import Blueprint, request, jsonify, session
import cloudinary
import cloudinary.uploader
import os
from db import get_db_connection
import requests
from io import BytesIO

# Create the Blueprint here
upload_routes = Blueprint("upload", __name__)

# Configure Cloudinary
cloudinary.config(cloudinary_url=os.getenv("CLOUDINARY_URL"))
print(cloudinary.config().cloud_name)

@upload_routes.route("/upload/<int:dataset_id>", methods=["POST"])
def upload_images():
    if not session.get("user_id"):
        return jsonify({"error": "Unauthorized"}), 401

    if 'files' not in request.files:
        return jsonify({"error": "No files provided"}), 400

    files = request.files.getlist('files')
    dataset_id = request.view_args['dataset_id']

    # Verify dataset belongs to user
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        with conn.cursor() as cursor:
            # Check if dataset belongs to user's project
            cursor.execute("""
                SELECT d.dataset_id 
                FROM dataset d 
                JOIN projects p ON d.project_id = p.project_id 
                WHERE d.dataset_id = %s AND p.user_id = %s
            """, (dataset_id, session.get("user_id")))
            
            if not cursor.fetchone():
                return jsonify({"error": "Dataset not found or unauthorized"}), 404

            uploaded_images = []
            for file in files:
                if file:
                    # Upload to Cloudinary
                    try:
                        upload_result = cloudinary.uploader.upload(file)
                        image_url = upload_result['secure_url']
                        
                        # Store in database
                        cursor.execute("""
                            INSERT INTO image (
                                image_name,
                                image_urls,
                                dataset_id,
                                created_at
                            ) VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                            RETURNING image_id
                        """, (
                            file.filename,
                            [image_url],  # Store as array since your schema expects TEXT[]
                            dataset_id
                        ))
                        
                        image_id = cursor.fetchone()[0]
                        uploaded_images.append({
                            "image_id": image_id,
                            "filename": file.filename,
                            "url": image_url
                        })
                        
                    except Exception as e:
                        print(f"Upload error for {file.filename}: {str(e)}")
                        continue

            conn.commit()
            return jsonify({
                "message": f"Successfully uploaded {len(uploaded_images)} images",
                "images": uploaded_images
            }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@upload_routes.route("/dataset/<int:dataset_id>/images", methods=["GET"])
def get_dataset_images(dataset_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        with conn.cursor() as cursor:
            # Get all images from the dataset
            cursor.execute("""
                SELECT image_id, image_name, image_urls
                FROM image
                WHERE dataset_id = %s
            """, (dataset_id,))
            
            images = cursor.fetchall()
            
            if not images:
                return jsonify({"error": "No images found in dataset"}), 404

            image_data = []
            for img in images:
                image_id, image_name, image_urls = img
                # Get the first URL from the image_urls array
                image_url = image_urls[0] if image_urls else None
                
                if image_url:
                    try:
                        # Download image from Cloudinary
                        response = requests.get(image_url)
                        if response.status_code == 200:
                            # Create BytesIO object from image data
                            image_bytes = BytesIO(response.content)
                            
                            image_data.append({
                                "image_id": image_id,
                                "image_name": image_name,
                                "image_url": image_url,
                                "image_bytes": image_bytes
                            })
                    except Exception as e:
                        print(f"Error downloading image {image_id}: {str(e)}")
                        continue

            return jsonify({
                "dataset_id": dataset_id,
                "image_count": len(image_data),
                "images": [{
                    "image_id": img["image_id"],
                    "image_name": img["image_name"],
                    "image_url": img["image_url"]
                } for img in image_data]
            }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

def process_dataset_images(dataset_id):
    """
    Helper function to get images for processing
    Returns a list of BytesIO objects containing image data
    """
    conn = get_db_connection()
    if not conn:
        return None

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT image_id, image_urls
                FROM image
                WHERE dataset_id = %s
            """, (dataset_id,))
            
            images = cursor.fetchall()
            image_data = []
            
            for img in images:
                image_id, image_urls = img
                image_url = image_urls[0] if image_urls else None
                
                if image_url:
                    try:
                        response = requests.get(image_url)
                        if response.status_code == 200:
                            image_bytes = BytesIO(response.content)
                            image_data.append({
                                "image_id": image_id,
                                "image_bytes": image_bytes
                            })
                    except Exception as e:
                        print(f"Error downloading image {image_id}: {str(e)}")
                        continue
            
            return image_data
    except Exception as e:
        print(f"Database error: {str(e)}")
        return None
    finally:
        conn.close()