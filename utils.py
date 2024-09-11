from models import ResumeData
from pydantic import BaseModel
from typing import List, Optional, Union
from models import ResumeData
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
import fitz


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()

    print(text)
    return text


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
    resume_text = extract_text_from_pdf(pdf_path)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    parser = PydanticOutputParser(pydantic_object=ResumeData)

    prompt = PromptTemplate(
        template=(
            "You are an expert at parsing resumes. Extract the following structured information "
            "from the given resume text in the same language as the resume. "
            "You must extract only real, specific information about the individual. "
            "Ignore any generic placeholder text or template information. "
            "If certain information is missing or unclear, return null for that field.\n"
            "You must extract:\n"
            "1. Name (only the actual name of the individual, not any placeholder)\n"
            "2. Contact Information (only real contact details, not generic placeholders)\n"
            "3. Skills (only skills specifically mentioned for this individual)\n"
            "4. Work Experience (with details for each job such as role, company, dates)\n"
            "5. Education (degree, institution, dates)\n"
            "6. Languages spoken (return null if no languages are specifically mentioned)\n"
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
