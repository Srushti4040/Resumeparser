import spacy
#import os
import logging
import pymongo
from pymongo import MongoClient
import docx
from pdfminer.high_level import extract_text


class ResumeParser:
    def __init__(self, resume_file_path):
        self.resume_file_path = resume_file_path
        self.nlp = spacy.load("en_core_web_sm")

    def extract_name(self, doc):
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text
        return None

    def extract_skills(self, doc):
        
        self.skill_categories= {
            "Programming": ["python", "java", "javascript", "php", "c++"],
            "Web Development": ["html", "css", "javascript", "react", "angular"],
            "Database Administrator": ["sql", "mongodb", "postgresql", "firebase"],
            "Machine Learning": ["machine learning", "deep learning", "nlp", "tensorflow", "pytorch"],
            ".NET Developer": ["C#","ASP.NET"]}
    

        found_skills = {category: [] for category in self.skill_categories}
        for token in doc:
             for category, skills in self.skill_categories.items():
                if token.text.lower() in skills:
                    found_skills[category].append(token.text)
        return found_skills
        

    def parse_text_resume(self, resume_text):
        doc = self.nlp(resume_text)
        candidate_name = self.extract_name(doc)
        candidate_skills = self.extract_skills(doc)
        return candidate_name, candidate_skills

    def parse_pdf_resume(self):
        try:
            resume_text = extract_text(self.resume_file_path)
            return self.parse_text_resume(resume_text)

        except Exception as e:
            logging.error(f"Error parsing PDF resume: {str(e)}")
            return None, None
        
             
    def parse_resume(self):
        
     if self.resume_file_path.lower().endswith(".pdf"):
            return self.parse_pdf_resume()      

     else:                    
        try:
           with open(self.resume_file_path, "r", encoding="utf-8") as file:
               resume_text = file.read()

           doc = self.nlp(resume_text)

           candidate_name = self.extract_name(doc)
           candidate_skills = self.extract_skills(doc)

           return candidate_name, candidate_skills
    
        except FileNotFoundError:
            logging.error(f"Error: File not found at {self.resume_file_path}")
            return None, None
        except Exception as e:
            logging.error(f"Error parsing resume: {str(e)}")
            return None, None
    
        

if __name__ == "__main__":
    resume_file_path = r"C:\Resumes\Alok Srivastava (3).pdf"

    resume_parser = ResumeParser(resume_file_path)
    candidate_name, candidate_skills = resume_parser.parse_resume()

class ResumeDatabase:
    def __init__(self, db_uri, db_name):
        self.client = MongoClient(db_uri)
        self.db = self.client[db_name]
        self.create_collection()

    def create_collection(self):
        self.candidates_collection = self.db['candidates']

    def insert_candidate(self, name, skills):
        candidate_data = {
            'name': name,
            'skills': skills
        }
        self.candidates_collection.insert_one(candidate_data)

    def close_connection(self):
        self.client.close()

if __name__ == "__main__":
    
    db_uri = 'mongodb://localhost:27017/' 
    db_name = 'resume_database'

    resume_file_path = r"C:\Resumes\Alok Srivastava (3).pdf"

    resume_parser = ResumeParser(resume_file_path)
    candidate_name, candidate_skills = resume_parser.parse_resume()

    if candidate_name:
        print(f"Candidate Name: {candidate_name}")

        resume_database = ResumeDatabase(db_uri, db_name)
        resume_database.insert_candidate(candidate_name, candidate_skills)
        resume_database.close_connection()

    else:
        print("Candidate name not found in the resume.")

    if candidate_skills:
        print("Skills:")
        for category, skills in candidate_skills.items():
            if skills:
                print(f"{category}: {', '.join(skills)}")
            else:
                print(f"{category}: No skills found in this category.")
    else:
        print("No skills found in the resume.")
