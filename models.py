from pydantic import BaseModel, Field
from typing import List, Optional, Union


class ContactInformation(BaseModel):
    email: Optional[str] = Field(None, description="Email address")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
    phone_number: Optional[str] = Field(None, description="Phone number if mentioned")
    address: Optional[str] = Field(None, description="Physical address if mentioned")
    personal_website: Optional[str] = Field(None, description="Personal website URL")
    github: Optional[str] = Field(None, description="GitHub profile URL")


class Education(BaseModel):
    degree: Optional[str] = Field(
        None, description="Degree obtained or pursued if mentioned"
    )
    institution: Optional[str] = Field(
        None, description="Name of the educational institution"
    )
    city: Optional[str] = Field(
        None, description="City where the educational institution is located"
    )
    graduation_date: Optional[str] = Field(
        None, description="Date of graduation or expected graduation"
    )
    gpa: Optional[Union[float, str]] = Field(
        None, description="Grade Point Average, if mentioned"
    )
    achievements: Optional[Union[List[str], str]] = Field(
        None, description="List of academic achievements or honors"
    )


class Language(BaseModel):
    name: Optional[str] = Field(None, description="Name of the language")
    proficiency: Optional[str] = Field(
        None, description="Proficiency level (e.g., Native, Fluent, Intermediate)"
    )
    certifications: Optional[Union[List[str], str]] = Field(
        None,
        description="List of certifications or qualifications related to the language",
    )


class WorkExperience(BaseModel):
    company: Optional[str] = Field(None, description="Name of the company")
    position: Optional[str] = Field(None, description="Job title or position held")
    start_date: Optional[str] = Field(None, description="Start date of the job")
    end_date: Optional[str] = Field(
        None, description="End date of the job, or 'Present' if current"
    )
    responsibilities: Optional[List[str]] = Field(
        None, description="List of job responsibilities or achievements"
    )


class ResumeData(BaseModel):
    full_name: Optional[str] = Field(None, description="The full name of the person")
    contact_information: Optional[ContactInformation] = Field(
        None, description="Contact information with optional fields"
    )
    skills: Optional[List[str]] = Field(
        None, description="List of skills mentioned in the resume"
    )
    education: Optional[List[Education]] = Field(
        None, description="List of education entries"
    )
    work_experience: Optional[List[WorkExperience]] = Field(
        None, description="List of work experience entries"
    )
    languages: Optional[List[Language]] = Field(
        None, description="List of languages mentioned in the resume"
    )

