from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from Resume_Parser import ResumeParser

app = Flask(__name__)

app.config['MONGO_URI'] = 'mongodb://localhost:27017/resume_database'
mongo = PyMongo(app)

resume_parser = ResumeParser(r"C:\Resumes\Alok Srivastava (3).pdf")

@app.route('/candidates', methods=['GET'])
def get_candidates():
    candidates_collection = mongo.db.candidates
    candidates = candidates_collection.find()

    candidate_list = []
    for candidate in candidates:
        candidate_list.append({
            'name': candidate['name'],
            'skills': candidate['skills']
        })

    return jsonify({'candidates': candidate_list})

@app.route('/parse_resume', methods=['POST'])
def add_candidate():
    try:
        resume_file_path = request.json['resume_file_path']
        candidate_name, candidate_skills = resume_parser.parse_resume(resume_file_path)

        if candidate_name:
            candidates_collection = mongo.db.candidates
            candidates_collection.insert_one({
                'name': candidate_name,
                'skills': candidate_skills
            })

            return jsonify({'message': 'Candidate added successfully'})
        else:
            return jsonify({'message': 'Candidate name not found in the resume'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)