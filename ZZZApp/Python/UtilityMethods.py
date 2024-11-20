import os
import sys
import dotenv
from pathlib import Path
import socket
import requests
from io import BytesIO

from PySide6.QtCore import QPoint, QUrl, Qt
from PySide6.QtGui import QImage, QPainter, QPainterPath, Qt


class utilityMethods:
    def create_rounded_image_from_url(image_url, output_path, radius=7):
        try:
            
            # If we get a file:/// URL, we need to convert it to a path
            if image_url.startswith('file:///'):
                image_url = image_url[8:]  # Strip the file:/// prefix
                source_image = QImage(image_url)
            else:
                # Web URL case
                response = requests.get(image_url)
                source_image = QImage()
                source_image.loadFromData(response.content)

            if source_image.isNull():
                print("Failed to load image")
                return None
                
            # Create output image with same size and ARGB32 format
            output_image = QImage(source_image.size(), QImage.Format_ARGB32)
            output_image.fill(Qt.transparent)
            
            # Create painter for output image
            painter = QPainter(output_image)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Create rounded rectangle path
            path = QPainterPath()
            rect = output_image.rect()
            path.addRoundedRect(rect, radius, radius)
            
            # Set clipping path and draw
            painter.setClipPath(path)
            painter.drawImage(QPoint(0, 0), source_image)
            painter.end()
            
            # Save the result
            if not output_image.save(output_path):
                print("Failed to save output image")
                return None
            print(f"Image saved to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error processing image: {e}")
            return None

