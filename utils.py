from models import ResumeData
from pydantic import BaseModel
from typing import List, Optional, Union
from models import ResumeData
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
import fitz
import pytesseract
from PIL import Image
import io
import numpy as np
import cv2
from deskew import determine_skew
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

def preprocess_image(image):
    # Convert PIL Image to OpenCV format
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Deskew
    angle = determine_skew(gray)
    rotated = rotate_image(gray, angle)

    # Binarization
    thresh = cv2.threshold(rotated, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # Noise removal
    denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)

    return Image.fromarray(denoised)


def rotate_image(image, angle):
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )
    return rotated


def detect_language(text):
    try:
        lang = detect(text)
        if lang == "ar":
            return "ara"
        elif lang == "fr":
            return "fra"
        else:
            return "eng"
    except LangDetectException:
        return "eng"


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)

        page_text = page.get_text()

        if len(page_text.strip()) < 50:  # Adjust this threshold as needed
            print(f"Using OCR for page {page_num + 1}...")

            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Increase resolution
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            preprocessed_img = preprocess_image(img)

            initial_text = pytesseract.image_to_string(
                preprocessed_img, config="--oem 3 --psm 6 -l eng+ara+fra"
            )

            detected_lang = detect_language(initial_text)

            page_text = pytesseract.image_to_string(
                preprocessed_img, config=f"--oem 3 --psm 6 -l {detected_lang}"
            )

            print(f"Detected language: {detected_lang}")
        else:
            print(f"Extracting text directly from page {page_num + 1}...")
            detected_lang = detect_language(page_text)
            print(f"Detected language: {detected_lang}")

        text += page_text + "\n\n"

    return text.strip()


def extract_text_from_pdf_cloud(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)

        page_text = page.get_text()

        if len(page_text.strip()) < 50:  # Adjust this threshold as needed
            print(f"Using OCR for page {page_num + 1}...")

            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Increase resolution
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            preprocessed_img = preprocess_image(img)

            initial_text = pytesseract.image_to_string(
                preprocessed_img, config="--oem 3 --psm 6 -l eng+ara+fra"
            )

            detected_lang = detect_language(initial_text)

            page_text = pytesseract.image_to_string(
                preprocessed_img, config=f"--oem 3 --psm 6 -l {detected_lang}"
            )

            print(f"Detected language: {detected_lang}")
        else:
            print(f"Extracting text directly from page {page_num + 1}...")
            detected_lang = detect_language(page_text)
            print(f"Detected language: {detected_lang}")

        text += page_text + "\n\n"

    return text.strip()
def validate_and_clean_resume_data(resume_data: ResumeData) -> ResumeData:
    # List of common placeholder texts and domains
    placeholder_texts = [
        "reallygreatsite.com",
        "example.com",
        "domain.com",
        "Anywhere St.",
        "Any City",
        "+123-456",
        "123 Anywhere",
    ]

    def clean_string(value: Optional[str]) -> Optional[str]:
        if value and any(placeholder in value for placeholder in placeholder_texts):
            return None
        return value

    def clean_list(
        value: Optional[List[Union[str, BaseModel]]]
    ) -> Optional[List[Union[str, BaseModel]]]:
        if value:
            cleaned = [
                item
                for item in value
                if not any(
                    placeholder in str(item) for placeholder in placeholder_texts
                )
            ]
            return cleaned if cleaned else None
        return None

    # Clean contact information
    if resume_data.contact_information:
        resume_data.contact_information.email = clean_string(
            resume_data.contact_information.email
        )
        resume_data.contact_information.phone_number = clean_string(
            resume_data.contact_information.phone_number
        )
        resume_data.contact_information.address = clean_string(
            resume_data.contact_information.address
        )
        resume_data.contact_information.linkedin = clean_string(
            resume_data.contact_information.linkedin
        )
        resume_data.contact_information.personal_website = clean_string(
            resume_data.contact_information.personal_website
        )
        resume_data.contact_information.github = clean_string(
            resume_data.contact_information.github
        )

    # Clean other fields
    resume_data.full_name = clean_string(resume_data.full_name)
    resume_data.skills = clean_list(resume_data.skills)

    # Clean work experience
    if resume_data.work_experience:
        cleaned_experience = []
        for exp in resume_data.work_experience:
            exp.company = clean_string(exp.company)
            exp.position = clean_string(exp.position)
            exp.start_date = clean_string(exp.start_date)
            exp.end_date = clean_string(exp.end_date)
            exp.responsibilities = clean_list(exp.responsibilities)
            if any(
                [
                    exp.company,
                    exp.position,
                    exp.start_date,
                    exp.end_date,
                    exp.responsibilities,
                ]
            ):
                cleaned_experience.append(exp)
        resume_data.work_experience = cleaned_experience if cleaned_experience else None

    # Clean education
    if resume_data.education:
        cleaned_education = []
        for edu in resume_data.education:
            edu.degree = clean_string(edu.degree)
            edu.institution = clean_string(edu.institution)
            edu.city = clean_string(edu.city)
            edu.graduation_date = clean_string(edu.graduation_date)
            edu.achievements = clean_list(edu.achievements)
            if any(
                [
                    edu.degree,
                    edu.institution,
                    edu.city,
                    edu.graduation_date,
                    edu.achievements,
                ]
            ):
                cleaned_education.append(edu)
        resume_data.education = cleaned_education if cleaned_education else None

    # Clean languages
    if resume_data.languages:
        cleaned_languages = []
        for lang in resume_data.languages:
            lang.name = clean_string(lang.name)
            lang.proficiency = clean_string(lang.proficiency)
            lang.certifications = clean_list(lang.certifications)
            if any([lang.name, lang.proficiency, lang.certifications]):
                cleaned_languages.append(lang)
        resume_data.languages = cleaned_languages if cleaned_languages else None

    return resume_data


def parse_resume(pdf_path):
    resume_text = extract_text_from_pdf_cloud(pdf_path)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    parser = PydanticOutputParser(pydantic_object=ResumeData)

    prompt = PromptTemplate(
        template=(
            "You are an expert at parsing resumes, capable of handling both well-structured digital PDFs "
            "and potentially disorganized text from scanned PDFs processed by OCR. Extract the following "
            "structured information from the given resume text in the same language as the resume.\n\n"
            "Important guidelines:\n"
            "1. Extract only real, specific information about the individual.\n"
            "2. Ignore any generic placeholder text or template information.\n"
            "3. If certain information is missing, unclear, or can't be confidently determined, return null for that field.\n"
            "4. The order of information might not be preserved in scanned PDFs. Look for relevant information throughout the entire text.\n"
            "5. Be prepared to handle inconsistent formatting, potential OCR errors, and fragmented text.\n"
            "6. Use context clues to determine the correct category for each piece of information.\n\n"
            "Extract the following:\n"
            "1. Name (only the actual name of the individual, not any placeholder)\n"
            "2. Contact Information (only real contact details, not generic placeholders)\n"
            "3. Skills (only skills specifically mentioned for this individual)\n"
            "4. Work Experience (with details for each job such as role, company, dates if available)\n"
            "5. Education (degree, institution, dates if available)\n"
            "6. Languages spoken (return null if no languages are specifically mentioned)\n\n"
            "For Work Experience and Education:\n"
            "- If dates are unclear or in an unusual format, interpret them as best as possible or omit if too ambiguous.\n"
            "- If the order of jobs or education entries is unclear, arrange them in the most logical order based on available information.\n\n"
            "Ensure that the extracted data follows this exact format: {format_instructions}\n\n"
            "Resume Text:\n{resume_text}\n\n"
            "Respond in JSON format."
        ),
        input_variables=["resume_text"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    chain = prompt | llm | parser

    parsed_data = chain.invoke({"resume_text": resume_text})

    cleaned_parsed_data = validate_and_clean_resume_data(parsed_data)

    return cleaned_parsed_data
