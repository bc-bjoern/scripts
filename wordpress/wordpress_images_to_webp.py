#!/usr/bin/env python3
import os
from urllib.parse import urlparse, urlunparse
from PIL import Image
import mysql.connector

"""
WordPress Image Conversion Script

This script connects to a WordPress database, retrieves image attachments,
converts them to WebP format, and updates the database with the new paths and metadata.

Usage:
1. Ensure that the script is configured with the correct database and file paths.
2. Run the script to process image attachments in the database.

Author: Björn
Date: 05.10.2023

"""

# Define the document root and uploads path
docroot = ""
uploads_path = "/wp-content/uploads"

# Database configuration
db_host = "localhost"
db_user = ""
db_password = ""
db_name = ""

exclude_images = ['1.png', '2.png', '3.png']

try:
    # Connect to the MySQL database
    conn = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )

    cursor = conn.cursor()

    # Select all image attachments from the wp_posts table
    cursor.execute("SELECT ID, post_title, post_mime_type, guid FROM wp_posts WHERE post_type = 'attachment' AND (post_mime_type = 'image/jpeg' OR post_mime_type = 'image/png')")
    results = cursor.fetchall()

    for row in results:
        post_id, post_title, post_mime_type, guid = row
        url = urlparse(guid)
        url_path = url.path

        # exclude
        filename = os.path.basename(file_path)
        if should_exclude_image(filename):
            print(f"Das Bild {filename} wird ausgeschlossen.")
            continue

        # Construct the absolute path to the image file
        image_path = os.path.join(docroot, url_path.lstrip('/'))

        if os.path.isfile(image_path):
            if post_mime_type == 'image/jpeg':
                image = Image.open(image_path)
                webp_path = image_path.replace('.jpg', '.webp').replace('.jpeg', '.webp')
                image.save(webp_path, 'webp')
            elif post_mime_type == 'image/png':
                image = Image.open(image_path)
                webp_path = image_path.replace('.png', '.webp')
                image.save(webp_path, 'webp')

            # Check if the updated path still contains the uploads directory
            if uploads_path in webp_path:
                # Extract the relative path within the uploads directory
                webp_file_path = webp_path.split(uploads_path, 1)[1].lstrip("/")
                webp_uri = urlunparse((url.scheme, url.netloc, uploads_path + "/" + webp_file_path, url.params, url.query, url.fragment))
                webp_file_name = os.path.splitext(os.path.basename(webp_path))[0]


                # Update the wp_posts table with the new paths
                update_query = "UPDATE wp_posts SET post_title = %s, guid = %s, post_mime_type = 'image/webp' WHERE ID = %s"
                cursor.execute(update_query, (webp_file_name, webp_uri, post_id))

                # Update the wp_postmeta table with the new file path
                update_meta_query = "UPDATE wp_postmeta SET meta_value = %s WHERE post_id = %s AND meta_key = '_wp_attached_file'"
                cursor.execute(update_meta_query, (webp_file_path, post_id))
                print("Changed "+image_path+" to "+webp_path)
        else:
            print(image_path + " doesn't exist")

    # Commit changes to the database
    conn.commit()

except mysql.connector.Error as err:
    print(f"Database error: {err}")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals() and conn.is_connected():
        conn.close()
