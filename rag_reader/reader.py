import os
import csv

from langchain.document_loaders import (
    CSVLoader,
    EverNoteLoader,
    PyMuPDFLoader,
    TextLoader,
    UnstructuredEmailLoader,
    UnstructuredEPubLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
    UnstructuredODTLoader,
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader,
)

class reader:
    def __init__(self, document_type: str = "text", verbose: bool = True):
        self.verboseprint = print if verbose else lambda *a: None

        try:
            self.document_type = document_type
            self.current_directory = os.getcwd()

            self.LOADER_MAPPING = {
                ".csv": (CSVLoader, {}),
                ".doc": (UnstructuredWordDocumentLoader, {}),
                ".docx": (UnstructuredWordDocumentLoader, {}),
                ".enex": (EverNoteLoader, {}),
                ".epub": (UnstructuredEPubLoader, {}),
                ".html": (UnstructuredHTMLLoader, {}),
                ".md": (UnstructuredMarkdownLoader, {}),
                ".odt": (UnstructuredODTLoader, {}),
                ".pdf": (PyMuPDFLoader, {}),
                ".ppt": (UnstructuredPowerPointLoader, {}),
                ".pptx": (UnstructuredPowerPointLoader, {}),
                ".txt": (TextLoader, {"encoding": "utf8"}),
                ".log": (TextLoader, {"encoding": "utf8"}),  # Added loader for .log files
                # Add more mappings for other file extensions and loaders as needed
            }
            self.verboseprint("READER: Reader initialised successfully")
        except Exception as e:
            self.verboseprint(f"READER: Reader initialization failed. Error: {str(e)}")

    def load_document(self, document_location: str) -> dict:
        """Loads the file into one or multiple langchain Documents"""

        ext = "." + document_location.rsplit(".", 1)[-1]
        if ext in self.LOADER_MAPPING:
            loader_class, loader_args = self.LOADER_MAPPING[ext]
            loader = loader_class(document_location, **loader_args)
            documents = loader.load()
            self.verboseprint(f"READER: {document_location} Loaded successfully.")

            doc = []
            document_name = ""
            document_type = ext

            for document in documents:
                doc.append(document.page_content)
                document_name = document.metadata["source"]

            return_obj = (doc, document_name, document_type)
            return return_obj

        else:
            raise ValueError(f"Unsupported file extension '{ext}'")
    
    def convert_to_csv(self, document_content: list, output_csv: str):
        """Converts the document content to a CSV file."""
        
        try:
            with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                for line in document_content:
                    writer.writerow([line])
            self.verboseprint(f"READER: Document converted to {output_csv} successfully.")
        except Exception as e:
            self.verboseprint(f"READER: Conversion to CSV failed. Error: {str(e)}")

