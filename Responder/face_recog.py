import os
import cv2
import numpy as np
import face_recognition
import streamlit as st
from collections import Counter
import time
import boto3
from botocore.exceptions import NoCredentialsError
from config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION_NAME

class FaceIdentifier:
    def __init__(self, known_faces_folder='known_faces'):
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_faces_folder = known_faces_folder
        self.bucket_name = 'reponder'
        self.load_known_faces_from_s3()


    def load_known_faces_from_s3(self):
        """
        Retrieves images from S3, converts them to face encodings, and stores them.
        """
        image_extensions = ['.png', '.jpg', '.jpeg']
        try:
            s3 = boto3.client(
                's3',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name=AWS_REGION_NAME
            )
            response = s3.list_objects_v2(Bucket=self.bucket_name)
            print("Response:", response)
            if 'Contents' in response:
                for obj in response['Contents']:
                    key = obj['Key']
                    if any(key.lower().endswith(ext) for ext in image_extensions):
                        try:
                            # Download the image from S3 to memory
                            local_file_path = os.path.join('known_faces',key)
                            image_object = s3.download_file(self.bucket_name, key, local_file_path)
                            # image_content = image_object['Body'].read()

                            # Load image from memory
                            image = face_recognition.load_image_file(local_file_path)
                            encoding = face_recognition.face_encodings(image)

                            if len(encoding) > 0:
                                self.known_face_encodings.append(encoding[0])
                                # Extract name from the key (filename)
                                filename = key.split('/')[-1]  # Get the filename part
                                name = os.path.splitext(filename)[0]
                                self.known_face_names.append(name)
                            else:
                                print(f"No face found in {key}")
                        except Exception as e:
                            print(f"Error processing image {key}: {e}")

            # Handle paginated results
            while response['IsTruncated']:
                continuation_token = response['NextContinuationToken']
                response = s3.list_objects_v2(Bucket=self.bucket_name, Prefix=self.prefix, ContinuationToken=continuation_token)
                if 'Contents' in response:
                    for obj in response['Contents']:
                        key = obj['Key']
                        if any(key.lower().endswith(ext) for ext in image_extensions):
                            try:
                                local_file_path = os.path.join('known_faces',key)
                                # Download the image from S3 to memory
                                image_object = s3.download_file(self.bucket_name, key, local_file_path)
                                # image_content = image_object['Body'].read()

                                # Load image from memory
                                image = face_recognition.load_image_file(local_file_path)
                                encoding = face_recognition.face_encodings(image)

                                if len(encoding) > 0:
                                    self.known_face_encodings.append(encoding[0])
                                    # Extract name from the key (filename)
                                    filename = key.split('/')[-1]  # Get the filename part
                                    name = os.path.splitext(filename)[0]
                                    self.known_face_names.append(name)
                                else:
                                    print(f"No face found in {key}")
                            except Exception as e:
                                print(f"Error processing image {key}: {e}")

            print(f"Loaded {len(self.known_face_names)} known faces from S3")

        except NoCredentialsError:
            print("Error: AWS credentials not found. Please configure your AWS credentials.")
        except Exception as e:
            print(f"An error occurred while accessing S3: {e.__traceback__}")


    def run_recognition(self):
        """Runs face recognition for 10 seconds and returns the most frequent match"""
        video_capture = cv2.VideoCapture(0)
        start_time = time.time()
        detected_names = []

        while time.time() - start_time < 5:  # Run for 10 seconds
            ret, frame = video_capture.read()
            if not ret:
                break

            # Resize frame for faster processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            # Find all faces in current frame
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                # Scale back up face locations
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Compare with known faces
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.6)
                
                if True in matches:
                    first_match_index = matches.index(True)
                    name = self.known_face_names[first_match_index]
                    detected_names.append(name)

                # Draw bounding box and label
                if name:
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

            # st.image(frame, caption='Face Identification', use_container_width=True)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        video_capture.release()
        cv2.destroyAllWindows()

        # Return the most common detected name
        if detected_names:
            st.image(frame, caption='Face Identification', use_container_width=True)
            return Counter(detected_names).most_common(1)[0][0]
        return "Unknown"