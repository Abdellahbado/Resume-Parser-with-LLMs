# Resume Parser

This project is an AI-powered resume parsing tool that extracts key information from PDF resumes using language models and presents it in a user-friendly web interface.

## Features

- Parse PDF resumes to extract structured information
- Clean and validate extracted data to remove placeholder text
- Display parsed information in an interactive web interface
- Support for multiple languages

## Technologies Used

- Python 3.7+
- Streamlit for the web interface
- LangChain with Google's Generative AI for natural language processing
- PyMuPDF (fitz) for PDF text extraction
- Pydantic for data validation and settings management

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/Abdellahbado/Resume-Parser-with-LLMs
   cd Resume-Parser-with-LLMs
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the project root and add your Google AI API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

## Usage

1. Run the Streamlit app:
   ```
   streamlit run main.py
   ```

2. Open your web browser and navigate to the URL provided by Streamlit (usually `http://localhost:8501`).

3. Upload a PDF resume using the file uploader.

4. The parsed information will be displayed in an organized layout.

## Project Structure

- `main.py`: Contains the Streamlit web application code
- `utils.py`: Includes utility functions for PDF parsing and data cleaning
- `models.py`: Defines Pydantic models for structured resume data

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
