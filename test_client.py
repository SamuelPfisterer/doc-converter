#!/usr/bin/env python3
"""
Test client for the document conversion service.
"""

import argparse
import os
import requests
import sys
import time

def convert_document(file_path, target_format, url):
    """
    Send a document to the conversion service and save the result.
    
    Args:
        file_path: Path to the input document
        target_format: Target format (docx, pdf)
        url: Service URL
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return False
    
    filename = os.path.basename(file_path)
    output_filename = f"converted.{target_format}"
    
    print(f"Converting {filename} to {target_format}...")
    
    start_time = time.time()
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (filename, f)}
            params = {'format': target_format}
            
            response = requests.post(url, files=files, params=params)
            
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            with open(output_filename, 'wb') as f:
                f.write(response.content)
            
            print(f"Success! Conversion completed in {elapsed_time:.2f} seconds.")
            print(f"Output saved to {output_filename}")
            return True
        else:
            print(f"Error: HTTP {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Document Conversion Client')
    parser.add_argument('file', help='Path to the file to convert')
    parser.add_argument('--format', '-f', default='docx', choices=['docx', 'pdf'],
                        help='Target format (default: docx)')
    parser.add_argument('--url', '-u', default='http://localhost:8000/convert',
                        help='Service URL (default: http://localhost:8000/convert)')
    
    args = parser.parse_args()
    
    success = convert_document(args.file, args.format, args.url)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main() 