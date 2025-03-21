from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for flash messages

#Database setup
# Use an absolute path for the database
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'skills.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)



#Define a Skill model
class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)   # Prevent duplicate skills
    level = db.Column(db.String(50), nullable=False)

#create the database(run once and then comment out)
"""with app.app_context():
    db.drop_all()
    db.create_all()
    # Preload initial skills
    initial_skills = [
        Skill(name="Python", level="Intermediate"),
        Skill(name="Flask", level="Beginner"),
        Skill(name="HTML", level="Beginner"),
        Skill(name="SQL", level="Beginner"),
        Skill(name="CSS", level="Beginner"),
        Skill(name="Django", level="To Learn"),
        Skill(name="Git", level="Beginner")
    ]
    db.session.add_all(initial_skills)
    db.session.commit()"""

"""# Dictionary: Skill levels
skills_dict = {
    "Python": "Intermediate",
    "Flask": "Beginner",
    "HTML": "Beginner",
    "SQL": "Beginner",
    "CSS": "Beginner",
    "Django": "To Learn",
    "Git": "Beginner"
}

# Tuple: Fixed goals
goals = ("Reach 9 LPA", "Build a Web App", "Master Python")"""

# Initialize the database with skills if the table is empty
with app.app_context():
    # Create the tables if they don't exist
    db.create_all()

    # Check if the skill table is empty
    if Skill.query.count() == 0:
        initial_skills = [
            Skill(name="Python", level="Intermediate"),
            Skill(name="Flask", level="Beginner"),
            Skill(name="HTML", level="Beginner"),
            Skill(name="SQL", level="Beginner"),
            Skill(name="CSS", level="Beginner"),
            Skill(name="Django", level="To Learn"),
            Skill(name="Git", level="Beginner"),
            Skill(name="Vue.js", level="Intermediate"),
            Skill(name="JavaScript", level="Beginner"),
            Skill(name="React", level="Intermediate"),
            Skill(name="Node.js", level="Beginner")
        ]
        db.session.add_all(initial_skills)
        db.session.commit()
        print("Initialized database with 11 skills")

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/skills", methods=["GET", "POST"])
def skills():
    if request.method == "POST":
        new_skill = request.form["skill"]
        new_level = request.form["level"]
        # Check for duplicate skill
        if Skill.query.filter_by(name=new_skill).first():
            flash(f"Skill '{new_skill}' already Exists!", "error")
            return redirect(url_for("skills"))
        skill_entry = Skill(name=new_skill, level=new_level)
        try:
            db.session.add(skill_entry)
            db.session.commit()
            flash(f"Added {new_skill} ({new_level}) successfully", "success")#success message
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding skill: {str(e)}", "error")
        return redirect(url_for("skills")) #redirect to /skills
    skills_list = Skill.query.all()  #fetch all skill from DB
    print(f"Skills fetched: {[f'{skill.name} ({skill.level})' for skill in skills_list]}")  # Debug
    return render_template("skills.html", skills_list=skills_list)

@app.route("/goals")
def goals_route():
    goals = ("Reach 9 LPA", "Build a web app", "Master Python")
    return render_template("goals.html", goals=goals)


#API routes
@app.route("/api/skills", methods=["GET"])
def get_skills():
    try:
        skills_list = Skill.query.all()
        print(f"API GET - Skills fetched: {[f'{skill.name} ({skill.level})' for skill in skills_list]}")
        skills_json = [{"id": skill.id, "name": skill.name, "level": skill.level} for skill in skills_list]
        print(f"API GET - JSON response: {skills_json}")
        return jsonify(skills_json)
    except Exception as e:
        print(f"API GET - Error:{str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/skills", methods=["POST"])
def add_skills_api():
    try:
        data = request.get_json()
        print(f"API POST - Received data: {data}")
        if not data or "name" not in data or "level" not in data:
            return jsonify({"error": "Missing name or level"}), 400
        # Check for duplicate skill
        if Skill.query.filter_by(name=data['name']).first():
            return jsonify({"error": f"Skill '{data['name']}' already Exists!"}), 400
        new_skill = Skill(name=data["name"], level=data["level"])
        db.session.add(new_skill)
        db.session.commit()
        print(f"API POST - Added: {data['name']} ({data['level']})")
        return jsonify({"message": f"Added {data['name']} ({data['level']})"}), 201
    except Exception as e:
        print(f"API POST - Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)