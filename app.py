from flask import Flask, request, render_template, redirect, session, url_for, send_from_directory
from flask_session import Session
from flask_pymongo import PyMongo
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from bs4 import BeautifulSoup 
from werkzeug.utils import secure_filename
from datetime import datetime
import os, random, string
from flask_mail import Mail, Message
from pymongo import MongoClient

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb+srv://admin:5ARnXB9J82HWp9i@cluster0.6idhh.mongodb.net/student"  # Replace with your MongoDB connection string
mongo = PyMongo(app)
app.secret_key='kumarvenkatesh'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'

mail = Mail(app)

from flask import Flask, request, session, render_template, redirect
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash
import random
import string
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'
mail = Mail(app)

def object_id_converter(doc):
    doc["_id"] = str(doc["_id"])  
    return doc

mail = Mail(app)

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method=='POST':

        try:
            student_data = request.form  
            name = student_data.get('name')
            email = student_data.get('email')
            existing_user= mongo.db.student.find_one({'email': email})
            if existing_user:
                return redirect('/login', message='User Already Exists!')
            password = student_data.get('password')
            mobile = student_data.get('mobile')
            country = student_data.get('country')
            college = student_data.get('college')
            yop = student_data.get('yop')
            gender = student_data.get('gender')
            dob = student_data.get('dob')

            hashed_password = generate_password_hash(password)

            student = {
                "name": name,
                "email": email,
                "password": hashed_password,
                "mobile": mobile,
                "country": country,
                "college": college,
                "yop": yop,
                "gender": gender,
                "dob": dob
            }

            student_id = mongo.db.student.insert_one(student).inserted_id
            return redirect('/login')
        except Exception as e:
            print('Error', e)
            return render_template('reg.html')
    return render_template('reg.html')
    
@app.route("/")
def index():
    if 'user' not in session:
        return redirect('/login')
    user = mongo.db.student.find_one({'email': session['user']})
    return render_template("home.html", user=user)

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = mongo.db.student.find_one({"email": email})
        
        if not user:  # Check if user is found
            return render_template("login.html", message="User not found")

        if check_password_hash(user['password'], password):
            session['email'] = user['email']  # Only set session after checking user exists
            return redirect("/home")

    return render_template("login.html")

@app.route('/forgot-password')
def fpswd():
    return render_template('fpswd.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/career', methods=['POST', 'GET'])
def car():
    email = session.get('email')
    if not email:
        return redirect('/login')  # Ensure the user is logged in

    # Check if the career is already set in the database or session
    career = session.get('career')
    if not career:
        # If career is not in session, check the database
        student = mongo.db.student.find_one({"email": email})
        if student and "career" in student:
            # If career exists in the database, set it in the session
            session['career'] = student['career']
            return redirect('/chosen')  # Redirect to /chosen

    if request.method == 'POST':
        # Handle form submission for career selection
        career = request.form.get('career')
        if career:
            # Update career in the database
            mongo.db.student.update_one(
                {"email": email},
                {"$set": {"career": career}},
                upsert=True
            )
            # Update session with the selected career
            session['career'] = career
            return redirect('/chosen')  # Redirect to /chosen after setting career
        else:
            # Handle case where no career is selected
            return render_template('career.html', message="Please select a career.")

    # Redirect to /chosen if career is already set
    if career:
        return redirect('/chosen')

    # Render career selection page if no career is set
    return render_template('career.html')


@app.route('/logout')
def logout():
    session.pop('email', None)  # Ensure the correct session key is cleared
    return redirect('/')

@app.route('/chosen', methods=['GET'])
def chosen():
    email = session.get('email')  # Get the email from session
    if not email:
        return redirect('/login')  # Redirect to login if email is not found in session
    
    # Fetch the user's career from the database
    student = mongo.db.student.find_one({"email": email})
    if student and "career" in student:
        career = student['career']
        return render_template('chosen.html', career=career)  # Display chosen career
    else:
        return redirect('/career')  # Redirect to career selection if none is set


@app.route('/skills', methods=['GET'])
def skills():
    email = session.get('email')
    if not email:
        return redirect('/login')  # Redirect to login if user is not logged in

    # Fetch the selected career from the database
    student = mongo.db.student.find_one({"email": email})
    career = student.get("career") if student else None

    # Skills data stored in a dictionary
    skills_data = {
    "software-developer": [
        "Programming in Python, Java, C++",
        "Version Control (Git, GitHub)",
        "Software Development Life Cycle",
        "Problem Solving and Debugging",
        "Agile Methodologies"
    ],
    "data-analyst": [
        "Data Visualization (Tableau, Power BI)",
        "SQL and Database Management",
        "Statistical Analysis",
        "Excel and Spreadsheet Proficiency",
        "Data Cleaning and Preprocessing"
    ],
    "ai-ml-specialist": [
        "Deep Learning Frameworks (TensorFlow, PyTorch)",
        "Machine Learning Algorithms",
        "Data Preprocessing and Feature Engineering",
        "Natural Language Processing",
        "Model Deployment and Optimization"
    ],
    "web-developer": [
        "HTML, CSS, JavaScript",
        "Frontend Frameworks (React, Angular)",
        "Backend Technologies (Node.js, Django)",
        "Responsive Design",
        "API Integration"
    ],
    "mobile-app-developer": [
        "Kotlin or Swift Programming",
        "Cross-Platform Development (Flutter, React Native)",
        "UI/UX for Mobile",
        "App Store Optimization",
        "RESTful APIs"
    ],
    "cloud-engineer": [
        "Cloud Platforms (AWS, Azure, GCP)",
        "Infrastructure as Code (Terraform, Ansible)",
        "Networking Concepts",
        "Security in Cloud Environments",
        "CI/CD Pipelines"
    ],
    "cybersecurity-analyst": [
        "Network Security",
        "Incident Response",
        "Risk Assessment and Mitigation",
        "Encryption and Cryptography",
        "Ethical Hacking"
    ],
    "system-administrator": [
        "System Configuration and Troubleshooting",
        "Server Management (Linux, Windows)",
        "Networking Protocols",
        "Backup and Recovery",
        "Shell Scripting"
    ],
    "network-engineer": [
        "Routing and Switching",
        "Network Design and Implementation",
        "Firewalls and Security",
        "LAN/WAN Management",
        "Network Troubleshooting"
    ],
    "database-administrator": [
        "Database Installation and Configuration",
        "SQL Query Optimization",
        "Backup and Recovery Solutions",
        "Database Security",
        "Performance Tuning"
    ],
    "hardware-engineer": [
        "Circuit Design",
        "Microprocessors and Embedded Systems",
        "PCB Design Tools",
        "Hardware Testing",
        "Signal Processing"
    ],
    "electrical-engineer": [
        "Power Systems",
        "Control Systems",
        "Electrical Circuit Analysis",
        "Renewable Energy Technologies",
        "Instrumentation"
    ],
    "civil-engineer": [
        "Structural Analysis",
        "Construction Management",
        "AutoCAD and Revit",
        "Surveying Techniques",
        "Material Testing"
    ],
    "mechanical-engineer": [
        "CAD Tools (SolidWorks, AutoCAD)",
        "Thermodynamics and Fluid Mechanics",
        "Manufacturing Processes",
        "Material Science",
        "Finite Element Analysis (FEA)"
    ],
    "automobile-engineer": [
        "Automotive Design",
        "Vehicle Dynamics",
        "Engine Systems",
        "Hybrid and Electric Vehicles",
        "Diagnostics and Maintenance"
    ],
    "biomedical-engineer": [
        "Medical Imaging Technologies",
        "Biomaterials",
        "Biomechanics",
        "Regulatory Compliance",
        "Healthcare Software"
    ],
    "chemical-engineer": [
        "Chemical Process Design",
        "Heat Transfer and Thermodynamics",
        "Safety and Risk Management",
        "Process Simulation Tools",
        "Catalysis"
    ],
    "industrial-engineer": [
        "Process Optimization",
        "Lean Manufacturing",
        "Ergonomics",
        "Supply Chain Management",
        "Quality Control"
    ],
    "architect": [
        "Building Design and Drafting",
        "3D Modeling (SketchUp, Revit)",
        "Urban Planning",
        "Construction Materials",
        "Structural Analysis"
    ],
    "product-designer": [
        "Sketching and Prototyping",
        "3D Modeling (Fusion 360, Rhino)",
        "Material Knowledge",
        "Design Thinking",
        "User Research"
    ],
    "quality-analyst": [
        "Test Case Development",
        "Automation Testing Tools",
        "Bug Tracking",
        "Agile Methodology",
        "Performance Testing"
    ],
    "business-analyst": [
        "Requirement Gathering",
        "Process Analysis",
        "Stakeholder Communication",
        "Data Visualization Tools",
        "Project Management"
    ],
    "project-manager": [
        "Project Planning",
        "Resource Allocation",
        "Risk Management",
        "Agile and Scrum Methodologies",
        "Communication Skills"
    ],
    "consultant": [
        "Domain Expertise",
        "Strategic Thinking",
        "Client Management",
        "Data Analysis",
        "Presentation Skills"
    ],
    "research-scientist": [
        "Experimental Design",
        "Data Analysis",
        "Scientific Writing",
        "Specialized Lab Techniques",
        "Innovation Skills"
    ],
    "entrepreneur": [
        "Business Planning",
        "Market Research",
        "Leadership Skills",
        "Financial Management",
        "Problem Solving"
    ],
    "management": [
        "Strategic Thinking",
        "Organizational Behavior",
        "Marketing Principles",
        "HR Management",
        "Leadership Skills"
    ],
    "teacher-professor": [
        "Subject Expertise",
        "Lesson Planning",
        "Student Engagement",
        "Assessment and Feedback",
        "Research Skills"
    ],
    "government-jobs": [
        "General Awareness",
        "Quantitative Aptitude",
        "Logical Reasoning",
        "Current Affairs",
        "Writing Skills"
    ],
    "higher-studies": [
        "Research Methodologies",
        "Academic Writing",
        "Specialized Subject Knowledge",
        "Critical Thinking",
        "Time Management"
    ],
    "startup-founder": [
        "Entrepreneurship",
        "Business Development",
        "Networking Skills",
        "Innovation",
        "Leadership"
    ],
    "sales-engineer": [
        "Product Knowledge",
        "Client Engagement",
        "Sales Strategies",
        "Communication Skills",
        "Technical Presentations"
    ],
    "supply-chain-manager": [
        "Inventory Management",
        "Logistics Optimization",
        "Demand Forecasting",
        "Vendor Management",
        "Data Analysis"
    ],
    "logistics-manager": [
        "Transportation Planning",
        "Warehouse Management",
        "Supply Chain Optimization",
        "Cost Control",
        "Communication Skills"
    ],
    "hr-specialist": [
        "Recruitment Strategies",
        "Employee Engagement",
        "Conflict Resolution",
        "Labor Laws",
        "Training and Development"
    ],
    "finance-analyst": [
        "Financial Modeling",
        "Data Analysis",
        "Budgeting and Forecasting",
        "Risk Assessment",
        "Investment Strategies"
    ],
    "data-scientist": [
        "Big Data Technologies",
        "Machine Learning Algorithms",
        "Data Wrangling",
        "Statistical Analysis",
        "Data Visualization"
    ],
    "game-developer": [
        "Game Engines (Unity, Unreal)",
        "3D Modeling",
        "Programming Languages (C#, C++)",
        "Animation",
        "Physics Simulation"
    ],
    "software-architect": [
        "System Design",
        "Architecture Patterns",
        "Scalability Solutions",
        "Programming Expertise",
        "Stakeholder Communication"
    ],
    "devops-engineer": [
        "CI/CD Pipelines",
        "Containerization (Docker, Kubernetes)",
        "Infrastructure as Code",
        "Cloud Platforms",
        "Monitoring and Logging"
    ],
    "research-and-development": [
        "Innovative Thinking",
        "Experimentation",
        "Technical Expertise",
        "Prototyping",
        "Patent Filing"
    ],
    "production-engineer": [
        "Manufacturing Processes",
        "Quality Control",
        "Production Planning",
        "Lean Manufacturing",
        "Material Handling"
    ],
    "testing-engineer": [
        "Manual and Automation Testing",
        "Test Plan Development",
        "Defect Reporting",
        "Performance Testing",
        "Regression Testing"
    ],
    "content-developer": [
        "Content Writing",
        "SEO Knowledge",
        "Content Management Tools",
        "Creative Thinking",
        "Grammar and Editing"
    ],
    "seo-specialist": [
        "Keyword Research",
        "Content Optimization",
        "Google Analytics",
        "Link Building",
        "SEO Tools"
    ],
    "marketing-manager": [
        "Marketing Campaigns",
        "Market Research",
        "Digital Marketing",
        "Brand Management",
        "Analytics"
    ],
    "user-experience-designer": [
        "Wireframing and Prototyping",
        "User Research",
        "Interaction Design",
        "Usability Testing",
        "Design Tools (Figma, Adobe XD)"
    ],
    "user-interface-designer": [
        "Visual Design",
        "Color Theory",
        "Typography",
        "UI Design Tools",
        "Design Guidelines"
    ],
    "product-manager": [
        "Market Analysis",
        "Roadmap Development",
        "Stakeholder Management",
        "Agile Methodologies",
        "Problem Solving"
    ],
    "business-development-manager": [
        "Sales Strategy",
        "Client Relationship Management",
        "Market Research",
        "Negotiation Skills",
        "Presentation Skills"
    ],
    "public-relations": [
        "Media Relations",
        "Crisis Management",
        "Press Releases"
    ]
    }
    # Fetch skills for the selected career
    career_skills = skills_data.get(career, None)

    if not career_skills:
        career_skills = ["No skills found for the selected career."]

    return render_template('skills.html', career=career, skills=career_skills)


career_courses = {
    "software-developer": [
        {"title": "Java Programming and Software Engineering Fundamentals", "link": "https://www.coursera.org/specializations/java-programming"},
        {"title": "Full Stack Web Development with React", "link": "https://www.coursera.org/specializations/full-stack-react"},
        {"title": "Python for Everybody", "link": "https://www.coursera.org/specializations/python"},
        {"title": "Introduction to Algorithms", "link": "https://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-006-introduction-to-algorithms-fall-2011/"},
        {"title": "Object-Oriented Programming in Java", "link": "https://www.edx.org/course/object-oriented-programming-in-java"}
    ],
    "data-analyst": [
        {"title": "Data Analysis with Python", "link": "https://www.coursera.org/learn/data-analysis-with-python"},
        {"title": "Data Visualization with Tableau", "link": "https://www.udemy.com/course/tableau-for-data-science/"},
        {"title": "Excel Skills for Business", "link": "https://www.coursera.org/specializations/excel"},
        {"title": "SQL for Data Analysis", "link": "https://www.datacamp.com/courses/intro-to-sql-for-data-science"},
        {"title": "Data Analyst Nanodegree", "link": "https://www.udacity.com/course/data-analyst-nanodegree--nd002"}
    ],
    "ai-ml-specialist": [
        {"title": "Machine Learning by Stanford University", "link": "https://www.coursera.org/learn/machine-learning"},
        {"title": "Deep Learning Specialization", "link": "https://www.coursera.org/specializations/deep-learning"},
        {"title": "Artificial Intelligence A-Z", "link": "https://www.udemy.com/course/artificial-intelligence-az/"},
        {"title": "Reinforcement Learning", "link": "https://www.udacity.com/course/reinforcement-learning--ud600"},
        {"title": "Introduction to TensorFlow for AI", "link": "https://www.coursera.org/learn/introduction-tensorflow"}
    ],
    "web-developer": [
        {"title": "The Web Developer Bootcamp", "link": "https://www.udemy.com/course/the-web-developer-bootcamp/"},
        {"title": "HTML, CSS, and JavaScript for Web Developers", "link": "https://www.coursera.org/learn/html-css-javascript-for-web-developers"},
        {"title": "React - The Complete Guide", "link": "https://www.udemy.com/course/react-the-complete-guide-incl-redux/"},
        {"title": "Build Responsive Real-World Websites", "link": "https://www.udemy.com/course/design-and-develop-a-killer-website-with-html5-and-css3/"},
        {"title": "Full Stack Web Development with Django", "link": "https://www.coursera.org/specializations/full-stack-development-django"}
    ],
    "mobile-app-developer": [
        {"title": "Android App Development", "link": "https://www.coursera.org/specializations/android-app-development"},
        {"title": "iOS App Development with Swift", "link": "https://developer.apple.com/swift/"},
        {"title": "Flutter & Dart - Complete Guide", "link": "https://www.udemy.com/course/learn-flutter-dart-to-build-ios-android-apps/"},
        {"title": "React Native - The Practical Guide", "link": "https://www.udemy.com/course/react-native-the-practical-guide/"},
        {"title": "Build a Mobile App with Google Firebase", "link": "https://www.udacity.com/course/firebase-in-a-weekend--ud0352"}
    ],
    "electrical-engineer": [
        {"title": "Electric Circuits", "link": "https://www.edx.org/course/circuits-and-electronics"},
        {"title": "Power Electronics", "link": "https://www.udemy.com/course/power-electronics/"},
        {"title": "Control Systems", "link": "https://www.coursera.org/learn/control-systems"},
        {"title": "Renewable Energy in Electrical Systems", "link": "https://www.futurelearn.com/courses/renewable-energy"},
        {"title": "Digital Signal Processing", "link": "https://www.udemy.com/course/digital-signal-processing/"}
    ],
    "civil-engineer": [
        {"title": "Construction Management", "link": "https://www.coursera.org/specializations/construction-management"},
        {"title": "Structural Engineering Basics", "link": "https://www.udemy.com/course/structural-engineering-basics/"},
        {"title": "Geotechnical Engineering", "link": "https://www.edx.org/course/introduction-to-geotechnical-engineering"},
        {"title": "AutoCAD for Civil Engineers", "link": "https://www.udemy.com/course/autocad-complete-guide/"},
        {"title": "Hydraulic Engineering", "link": "https://www.futurelearn.com/courses/hydraulic-engineering"}
    ],
    "mechanical-engineer": [
        {"title": "Mechanical Engineering and Design", "link": "https://www.coursera.org/specializations/mechanical-design"},
        {"title": "SolidWorks: Engineering Design", "link": "https://www.udemy.com/course/solidworks-complete-course/"},
        {"title": "Thermodynamics Basics", "link": "https://www.edx.org/course/introduction-to-thermodynamics"},
        {"title": "HVAC Systems Design", "link": "https://www.udemy.com/course/hvac-systems-design/"},
        {"title": "Robotics for Mechanical Engineers", "link": "https://www.udemy.com/course/robotics-for-beginners/"}  
    ],
    "automobile-engineer": [
        {"title": "Automotive Engineering Fundamentals", "link": "https://www.coursera.org/specializations/automotive-engineering"},
        {"title": "Vehicle Dynamics", "link": "https://www.udemy.com/course/vehicle-dynamics/"},
        {"title": "Electric Vehicle Design", "link": "https://www.edx.org/course/introduction-to-electric-vehicle-design"},
        {"title": "Internal Combustion Engines", "link": "https://www.coursera.org/learn/ic-engine"},
        {"title": "Advanced Driver Assistance Systems (ADAS)", "link": "https://www.udemy.com/course/adas-systems/"}  
    ],
    "biomedical-engineer": [
        {"title": "Introduction to Biomedical Engineering", "link": "https://www.coursera.org/learn/biomedical-engineering"},
        {"title": "Medical Imaging Basics", "link": "https://www.edx.org/course/introduction-to-medical-imaging"},
        {"title": "Biomechanics for Beginners", "link": "https://www.udemy.com/course/biomechanics-basics/"},
        {"title": "Biomedical Signal Processing", "link": "https://www.coursera.org/learn/biomedical-signal-processing"},
        {"title": "Wearable Medical Devices", "link": "https://www.futurelearn.com/courses/wearable-devices"}
    ],
    "chemical-engineer": [
        {"title": "Introduction to Chemical Engineering", "link": "https://ocw.mit.edu/courses/chemical-engineering/10-50-introduction-to-chemical-engineering-fall-2012/"},
        {"title": "Chemical Process Control", "link": "https://www.udemy.com/course/chemical-process-control/"},
        {"title": "Fluid Mechanics", "link": "https://www.coursera.org/learn/fluid-mechanics"},
        {"title": "Heat Transfer Operations", "link": "https://www.edx.org/course/heat-transfer-in-engineering"},
        {"title": "Polymer Engineering", "link": "https://www.udemy.com/course/polymer-engineering/"}  
    ],
    "industrial-engineer": [
        {"title": "Lean Manufacturing Principles", "link": "https://www.coursera.org/learn/lean-manufacturing"},
        {"title": "Operations Management", "link": "https://www.coursera.org/specializations/operations-management"},
        {"title": "Supply Chain Fundamentals", "link": "https://www.edx.org/course/supply-chain-fundamentals"},
        {"title": "Six Sigma Green Belt", "link": "https://www.udemy.com/course/six-sigma-green-belt/"},
        {"title": "Industrial Automation", "link": "https://www.udemy.com/course/industrial-automation/"}  
    ],
    "architect": [
        {"title": "Basics of Architectural Design", "link": "https://www.coursera.org/learn/architectural-design-basics"},
        {"title": "3D Modeling with Revit", "link": "https://www.udemy.com/course/revit-architecture-essentials/"},
        {"title": "History of Architecture", "link": "https://www.edx.org/course/introduction-to-architecture"},
        {"title": "Sustainable Design in Architecture", "link": "https://www.coursera.org/learn/sustainable-architecture"},
        {"title": "AutoCAD for Architects", "link": "https://www.udemy.com/course/autocad-for-architects/"}
    ],
    "product-designer": [
        {"title": "UI/UX Design Fundamentals", "link": "https://www.coursera.org/specializations/ui-ux-design"},
        {"title": "Adobe Illustrator for Designers", "link": "https://www.udemy.com/course/adobe-illustrator-course/"},
        {"title": "Product Design with Fusion 360", "link": "https://www.coursera.org/learn/product-design-fusion-360"},
        {"title": "Introduction to Human-Centered Design", "link": "https://www.edx.org/course/human-centered-design"},
        {"title": "Sketch for Designers", "link": "https://www.udemy.com/course/sketch-design-for-beginners/"}
    ],
    "quality-analyst": [
        {"title": "Software Testing Fundamentals", "link": "https://www.coursera.org/specializations/software-testing"},
        {"title": "Automation Testing with Selenium", "link": "https://www.udemy.com/course/selenium-webdriver-with-java/"},
        {"title": "Introduction to QA Testing", "link": "https://www.udemy.com/course/qa-testing-introduction/"},
        {"title": "JIRA for Quality Analysts", "link": "https://www.udemy.com/course/jira-for-software-testers/"},
        {"title": "Performance Testing Basics", "link": "https://www.coursera.org/learn/performance-testing"}
    ],
    "business-analyst": [
        {"title": "Business Analytics Specialization", "link": "https://www.coursera.org/specializations/business-analytics"},
        {"title": "Data Visualization for Business", "link": "https://www.udemy.com/course/data-visualization-for-business/"},
        {"title": "SQL for Business Analysis", "link": "https://www.udemy.com/course/sql-for-business-analysts/"},
        {"title": "Introduction to Business Intelligence", "link": "https://www.udemy.com/course/business-intelligence-introduction/"},
        {"title": "Excel for Business Analysts", "link": "https://www.coursera.org/learn/excel-business-analysts"}
    ],
        "project-manager": [
        {"title": "Project Management Essentials", "link": "https://www.coursera.org/specializations/project-management"},
        {"title": "Agile Project Management", "link": "https://www.udemy.com/course/agile-project-management/"},
        {"title": "PMP Certification Prep", "link": "https://www.udemy.com/course/pmp-certification-prep/"},
        {"title": "Risk Management in Projects", "link": "https://www.coursera.org/learn/project-risk-management"},
        {"title": "Microsoft Project Basics", "link": "https://www.udemy.com/course/microsoft-project-tutorial/"}
    ],
    "consultant": [
        {"title": "Consulting Foundations", "link": "https://www.udemy.com/course/consulting-foundations/"},
        {"title": "Management Consulting Basics", "link": "https://www.coursera.org/specializations/management-consulting"},
        {"title": "Presentation Skills for Consultants", "link": "https://www.udemy.com/course/presentation-skills-for-consultants/"},
        {"title": "Financial Modeling for Consultants", "link": "https://www.coursera.org/learn/financial-modeling"},
        {"title": "Problem Solving for Consultants", "link": "https://www.udemy.com/course/consulting-problem-solving/"}
    ],
    "research-scientist": [
        {"title": "Research Methods", "link": "https://www.coursera.org/learn/research-methods"},
        {"title": "Data Analysis in Scientific Research", "link": "https://www.udemy.com/course/data-analysis-science/"},
        {"title": "Publishing Research Papers", "link": "https://www.edx.org/course/research-paper-writing"},
        {"title": "Grant Writing for Scientists", "link": "https://www.udemy.com/course/grant-writing-for-scientists/"},
        {"title": "Lab Techniques for Researchers", "link": "https://www.udemy.com/course/lab-techniques/"}
    ],
    "entrepreneur": [
        {"title": "Entrepreneurship 101", "link": "https://www.coursera.org/specializations/entrepreneurship"},
        {"title": "Starting a Startup", "link": "https://www.udemy.com/course/starting-a-startup/"},
        {"title": "Lean Startup Methodology", "link": "https://www.udemy.com/course/lean-startup/"},
        {"title": "Business Plan Creation", "link": "https://www.coursera.org/learn/business-plan"},
        {"title": "Funding for Entrepreneurs", "link": "https://www.udemy.com/course/startup-funding/"}
    ],
    "management": [
        {"title": "Principles of Management", "link": "https://www.coursera.org/learn/principles-of-management"},
        {"title": "MBA Essentials", "link": "https://www.udemy.com/course/mba-essentials/"},
        {"title": "Human Resources Management", "link": "https://www.coursera.org/learn/human-resources"},
        {"title": "Strategic Management", "link": "https://www.udemy.com/course/strategic-management/"},
        {"title": "Marketing Management", "link": "https://www.coursera.org/specializations/marketing-management"}
    ],
    "teacher-professor": [
        {"title": "Teaching in the Digital Age", "link": "https://www.udemy.com/course/teaching-in-the-digital-age/"},
        {"title": "Instructional Design Basics", "link": "https://www.coursera.org/learn/instructional-design"},
        {"title": "Classroom Management", "link": "https://www.udemy.com/course/classroom-management/"},
        {"title": "Creating Online Courses", "link": "https://www.udemy.com/course/create-online-course/"},
        {"title": "Pedagogy in Higher Education", "link": "https://www.edx.org/course/teaching-strategies-in-higher-education"}
    ],
    "government-jobs": [
        {"title": "UPSC Preparation Guide", "link": "https://www.coursera.org/specializations/upsc-preparation"},
        {"title": "PSU Recruitment Basics", "link": "https://www.udemy.com/course/psu-exam-preparation/"},
        {"title": "Indian Polity", "link": "https://www.udemy.com/course/indian-polity/"},
        {"title": "Quantitative Aptitude for Government Exams", "link": "https://www.udemy.com/course/quantitative-aptitude/"},
        {"title": "General Knowledge and Current Affairs", "link": "https://www.udemy.com/course/gk-current-affairs/"}
    ],
    "higher-studies": [
        {"title": "GRE Preparation", "link": "https://www.coursera.org/specializations/gre-preparation"},
        {"title": "TOEFL Preparation", "link": "https://www.udemy.com/course/toefl-preparation/"},
        {"title": "Research Proposal Writing", "link": "https://www.coursera.org/learn/research-proposal"},
        {"title": "Scholarship Applications 101", "link": "https://www.udemy.com/course/scholarship-applications/"},
        {"title": "Graduate School Admission Tips", "link": "https://www.udemy.com/course/graduate-school-admissions/"}
    ],
    "startup-founder": [
        {"title": "Startup Essentials", "link": "https://www.coursera.org/specializations/startup-essentials"},
        {"title": "Building a Business Model", "link": "https://www.udemy.com/course/business-model-canvas/"},
        {"title": "Pitching to Investors", "link": "https://www.udemy.com/course/investor-pitching/"},
        {"title": "Legal Aspects for Startups", "link": "https://www.udemy.com/course/startup-legal-aspects/"},
        {"title": "Product Market Fit", "link": "https://www.coursera.org/learn/product-market-fit"}
    ],
    "sales-engineer": [
        {"title": "Technical Sales Fundamentals", "link": "https://www.udemy.com/course/technical-sales/"},
        {"title": "B2B Sales Strategies", "link": "https://www.coursera.org/learn/b2b-sales-strategies"},
        {"title": "Negotiation Skills for Sales Engineers", "link": "https://www.udemy.com/course/negotiation-skills-for-sales/"},
        {"title": "Understanding Product Lifecycles", "link": "https://www.coursera.org/learn/product-lifecycle"},
        {"title": "Customer Relationship Management (CRM)", "link": "https://www.udemy.com/course/customer-relationship-management/"}
    ],
    "supply-chain-manager": [
        {"title": "Supply Chain Fundamentals", "link": "https://www.coursera.org/specializations/supply-chain-management"},
        {"title": "Logistics and Operations Management", "link": "https://www.udemy.com/course/logistics-operations/"},
        {"title": "Inventory Management Basics", "link": "https://www.coursera.org/learn/inventory-management"},
        {"title": "Lean Supply Chain Principles", "link": "https://www.udemy.com/course/lean-supply-chain/"},
        {"title": "Global Supply Chain Challenges", "link": "https://www.edx.org/course/global-supply-chain-management"}
    ],
    "logistics-manager": [
        {"title": "Introduction to Logistics", "link": "https://www.udemy.com/course/introduction-to-logistics/"},
        {"title": "Warehouse Management", "link": "https://www.coursera.org/learn/warehouse-management"},
        {"title": "Transportation Logistics", "link": "https://www.udemy.com/course/transportation-logistics/"},
        {"title": "Fleet Management Fundamentals", "link": "https://www.udemy.com/course/fleet-management/"},
        {"title": "Strategic Logistics Planning", "link": "https://www.coursera.org/learn/strategic-logistics"}
    ],
    "hr-specialist": [
        {"title": "HR Management Essentials", "link": "https://www.coursera.org/learn/hr-management"},
        {"title": "Recruitment and Talent Acquisition", "link": "https://www.udemy.com/course/talent-acquisition/"},
        {"title": "Employee Onboarding and Retention", "link": "https://www.coursera.org/learn/employee-onboarding"},
        {"title": "Diversity and Inclusion in the Workplace", "link": "https://www.edx.org/course/diversity-and-inclusion"},
        {"title": "Labor Laws and Compliance", "link": "https://www.udemy.com/course/labor-laws-compliance/"}
    ],
    "finance-analyst": [
        {"title": "Financial Analysis Fundamentals", "link": "https://www.coursera.org/specializations/financial-analysis"},
        {"title": "Corporate Finance Essentials", "link": "https://www.udemy.com/course/corporate-finance/"},
        {"title": "Excel for Financial Modeling", "link": "https://www.coursera.org/learn/excel-financial-modeling"},
        {"title": "Accounting Basics for Finance Analysts", "link": "https://www.udemy.com/course/accounting-for-finance/"},
        {"title": "Investment Analysis and Portfolio Management", "link": "https://www.udemy.com/course/investment-analysis-portfolio-management/"}
    ],
    "data-scientist": [
        {"title": "Python for Data Science", "link": "https://www.coursera.org/learn/python-for-data-science"},
        {"title": "Data Visualization with Tableau", "link": "https://www.udemy.com/course/data-visualization-with-tableau/"},
        {"title": "Machine Learning A-Z", "link": "https://www.udemy.com/course/machinelearning/"},
        {"title": "Big Data Analytics", "link": "https://www.edx.org/course/big-data-analytics"},
        {"title": "Statistical Methods for Data Scientists", "link": "https://www.coursera.org/learn/statistics-for-data-science"}
    ],
    "game-developer": [
        {"title": "Game Development with Unity", "link": "https://www.udemy.com/course/unity-game-development/"},
        {"title": "2D and 3D Game Design", "link": "https://www.coursera.org/learn/game-design"},
        {"title": "Game AI Development", "link": "https://www.udemy.com/course/game-ai-development/"},
        {"title": "Mobile Game Development Basics", "link": "https://www.udemy.com/course/mobile-game-development/"},
        {"title": "Game Physics Essentials", "link": "https://www.udemy.com/course/game-physics/"}
    ],
    "software-architect": [
        {"title": "Software Architecture Essentials", "link": "https://www.coursera.org/specializations/software-architecture"},
        {"title": "Design Patterns in Software Development", "link": "https://www.udemy.com/course/design-patterns/"},
        {"title": "Cloud Architecture Basics", "link": "https://www.udemy.com/course/cloud-architecture/"},
        {"title": "Scalable System Design", "link": "https://www.udemy.com/course/scalable-system-design/"},
        {"title": "Microservices Architecture", "link": "https://www.coursera.org/learn/microservices-architecture"}
    ],
    "devops-engineer": [
        {"title": "DevOps Fundamentals", "link": "https://www.coursera.org/learn/devops-fundamentals"},
        {"title": "CI/CD Pipelines with Jenkins", "link": "https://www.udemy.com/course/ci-cd-pipelines/"},
        {"title": "Docker and Kubernetes Basics", "link": "https://www.udemy.com/course/docker-kubernetes/"},
        {"title": "Cloud DevOps on AWS", "link": "https://www.coursera.org/specializations/cloud-devops-aws"},
        {"title": "Infrastructure as Code with Terraform", "link": "https://www.udemy.com/course/terraform-iac/"}
    ],
    "research-and-development": [
    {"title": "Research Methodologies", "link": "https://www.coursera.org/learn/research-methodologies"},
    {"title": "Innovation Management", "link": "https://www.udemy.com/course/innovation-management/"},
    {"title": "Design of Experiments", "link": "https://www.coursera.org/learn/design-experiments"},
    {"title": "Advanced Materials Research", "link": "https://www.edx.org/course/advanced-materials"},
    {"title": "Patents and Intellectual Property", "link": "https://www.udemy.com/course/intellectual-property/"}
    ],
    "production-engineer": [
        {"title": "Lean Manufacturing Principles", "link": "https://www.udemy.com/course/lean-manufacturing/"},
        {"title": "Production and Operations Management", "link": "https://www.coursera.org/learn/operations-management"},
        {"title": "Six Sigma Green Belt", "link": "https://www.udemy.com/course/six-sigma-green-belt/"},
        {"title": "Factory Automation Basics", "link": "https://www.coursera.org/learn/factory-automation"},
        {"title": "Quality Control Systems", "link": "https://www.udemy.com/course/quality-control/"}
    ],
    "testing-engineer": [
        {"title": "Software Testing Fundamentals", "link": "https://www.coursera.org/learn/software-testing"},
        {"title": "Automation Testing with Selenium", "link": "https://www.udemy.com/course/selenium-testing/"},
        {"title": "API Testing with Postman", "link": "https://www.udemy.com/course/api-testing/"},
        {"title": "Performance Testing with JMeter", "link": "https://www.coursera.org/learn/performance-testing"},
        {"title": "Mobile Application Testing", "link": "https://www.udemy.com/course/mobile-testing/"}
    ],
    "content-developer": [
        {"title": "Content Creation Strategies", "link": "https://www.udemy.com/course/content-creation/"},
        {"title": "SEO Writing Techniques", "link": "https://www.coursera.org/learn/seo-writing"},
        {"title": "Storytelling for Content Creators", "link": "https://www.udemy.com/course/storytelling-content/"},
        {"title": "Video Content Creation", "link": "https://www.coursera.org/learn/video-content"},
        {"title": "Social Media Content Development", "link": "https://www.udemy.com/course/social-media-content/"}
    ],
    "seo-specialist": [
        {"title": "Search Engine Optimization (SEO)", "link": "https://www.coursera.org/specializations/seo"},
        {"title": "Google Analytics for Beginners", "link": "https://www.udemy.com/course/google-analytics/"},
        {"title": "Keyword Research and Optimization", "link": "https://www.coursera.org/learn/keyword-research"},
        {"title": "Technical SEO Fundamentals", "link": "https://www.udemy.com/course/technical-seo/"},
        {"title": "Link Building Strategies", "link": "https://www.udemy.com/course/link-building/"}
    ],
    "marketing-manager": [
        {"title": "Marketing Strategy Fundamentals", "link": "https://www.coursera.org/learn/marketing-strategy"},
        {"title": "Digital Marketing Specialization", "link": "https://www.udemy.com/course/digital-marketing/"},
        {"title": "Market Research Basics", "link": "https://www.coursera.org/learn/market-research"},
        {"title": "Brand Management Essentials", "link": "https://www.udemy.com/course/brand-management/"},
        {"title": "Social Media Marketing", "link": "https://www.udemy.com/course/social-media-marketing/"}
    ],
    "user-experience-designer": [
        {"title": "UX Design Fundamentals", "link": "https://www.coursera.org/learn/ux-design"},
        {"title": "User Research Techniques", "link": "https://www.udemy.com/course/user-research/"},
        {"title": "Wireframing and Prototyping", "link": "https://www.coursera.org/learn/wireframing"},
        {"title": "Accessibility in UX Design", "link": "https://www.udemy.com/course/ux-accessibility/"},
        {"title": "Advanced Interaction Design", "link": "https://www.coursera.org/learn/interaction-design"}
    ],
    "user-interface-designer": [
        {"title": "UI Design Basics", "link": "https://www.coursera.org/learn/ui-design"},
        {"title": "Figma for UI Design", "link": "https://www.udemy.com/course/figma-ui-design/"},
        {"title": "Mobile App UI Design", "link": "https://www.coursera.org/learn/mobile-ui-design"},
        {"title": "Typography in UI Design", "link": "https://www.udemy.com/course/ui-typography/"},
        {"title": "UI Design Patterns", "link": "https://www.udemy.com/course/ui-design-patterns/"}
    ],
    "product-manager": [
        {"title": "Product Management Essentials", "link": "https://www.coursera.org/learn/product-management"},
        {"title": "Agile Product Development", "link": "https://www.udemy.com/course/agile-product-development/"},
        {"title": "Roadmap Planning for Products", "link": "https://www.coursera.org/learn/product-roadmap"},
        {"title": "Customer-Centric Product Design", "link": "https://www.udemy.com/course/customer-centric-design/"},
        {"title": "Metrics for Product Success", "link": "https://www.udemy.com/course/product-metrics/"}
    ],
    "business-development-manager": [
        {"title": "Business Development Fundamentals", "link": "https://www.coursera.org/learn/business-development"},
        {"title": "Strategic Partnerships and Alliances", "link": "https://www.udemy.com/course/strategic-partnerships/"},
        {"title": "Sales Techniques for Growth", "link": "https://www.coursera.org/learn/sales-techniques"},
        {"title": "Pitching and Negotiation", "link": "https://www.udemy.com/course/pitching-negotiation/"},
        {"title": "Market Expansion Strategies", "link": "https://www.udemy.com/course/market-expansion/"}
    ],
    "public-relations": [
        {"title": "Introduction to Public Relations", "link": "https://www.coursera.org/learn/public-relations"},
        {"title": "Public Relations Strategy", "link": "https://www.udemy.com/course/pr-strategy"},
        {"title": "Corporate Communications and Public Relations", "link": "https://www.edx.org/course/corporate-communications"},
        {"title": "Media Relations Essentials", "link": "https://www.linkedin.com/learning/media-relations-essentials"},
        {"title": "Crisis Communication", "link": "https://www.skillshare.com/classes/crisis-communication/104385"},
    ],
    "event-manager": [
        {"title": "Event Planning Foundations", "link": "https://www.udemy.com/course/event-planning-foundations"},
        {"title": "Managing Successful Events", "link": "https://www.coursera.org/learn/event-management"},
        {"title": "Special Events Management", "link": "https://www.edx.org/course/special-events-management"},
        {"title": "Event Marketing Strategies", "link": "https://www.linkedin.com/learning/event-marketing-strategies"},
        {"title": "Certified Event Planning Professional", "link": "https://www.alison.com/course/certified-event-planning-professional"},
    ],
    "graphic-designer": [
        {"title": "Graphic Design Specialization", "link": "https://www.coursera.org/specializations/graphic-design"},
        {"title": "Adobe Illustrator for Beginners", "link": "https://www.udemy.com/course/adobe-illustrator-beginners"},
        {"title": "Creative Graphic Design Techniques", "link": "https://www.skillshare.com/classes/graphic-design/134679"},
        {"title": "Brand Identity Design", "link": "https://www.linkedin.com/learning/brand-identity-design"},
        {"title": "Design Principles and Visual Communication", "link": "https://www.edx.org/course/design-principles"},
    ],
    "media-planner": [
        {"title": "Media Planning and Strategy", "link": "https://www.udemy.com/course/media-planning-strategy"},
        {"title": "Essentials of Media Buying", "link": "https://www.coursera.org/learn/media-buying"},
        {"title": "Digital Media Planning", "link": "https://www.linkedin.com/learning/digital-media-planning"},
        {"title": "Effective Campaign Planning", "link": "https://www.skillshare.com/classes/campaign-planning/129401"},
        {"title": "Marketing and Media Analytics", "link": "https://www.edx.org/course/media-analytics"},
    ],
    "advertising-manager": [
        {"title": "Advertising and Society", "link": "https://www.coursera.org/learn/advertising-society"},
        {"title": "Integrated Marketing Communications", "link": "https://www.udemy.com/course/marketing-communications"},
        {"title": "Advertising Foundations", "link": "https://www.linkedin.com/learning/advertising-foundations"},
        {"title": "Creative Advertising Strategies", "link": "https://www.skillshare.com/classes/advertising-strategies/176854"},
        {"title": "Digital Advertising and Promotions", "link": "https://www.edx.org/course/digital-advertising"},
    ],
    "tourism-manager": [
        {"title": "Introduction to Tourism Management", "link": "https://www.coursera.org/learn/tourism-management"},
        {"title": "Sustainable Tourism Practices", "link": "https://www.edx.org/course/sustainable-tourism-practices"},
        {"title": "Hospitality and Tourism Marketing", "link": "https://www.udemy.com/course/hospitality-tourism-marketing"},
        {"title": "Tourism Strategy and Planning", "link": "https://www.skillshare.com/classes/tourism-strategy/138284"},
        {"title": "Tourism Industry Essentials", "link": "https://www.linkedin.com/learning/tourism-industry-essentials"},
    ],
    "logistics-engineer": [
        {"title": "Logistics and Supply Chain Management", "link": "https://www.coursera.org/specializations/supply-chain-management"},
        {"title": "Fundamentals of Logistics", "link": "https://www.udemy.com/course/fundamentals-of-logistics"},
        {"title": "Advanced Supply Chain Analytics", "link": "https://www.edx.org/course/supply-chain-analytics"},
        {"title": "Warehouse and Inventory Management", "link": "https://www.linkedin.com/learning/warehouse-management"},
        {"title": "Logistics Optimization Techniques", "link": "https://www.skillshare.com/classes/logistics-optimization/119345"},
    ],
    "telecommunications-engineer": [
        {"title": "Telecommunication Networks Essentials", "link": "https://www.coursera.org/learn/telecommunications"},
        {"title": "Wireless Communication Systems", "link": "https://www.udemy.com/course/wireless-communication"},
        {"title": "Advanced Networking Protocols", "link": "https://www.edx.org/course/advanced-networking"},
        {"title": "IoT and Telecommunications", "link": "https://www.linkedin.com/learning/iot-telecommunications"},
        {"title": "Fiber Optics and Communication", "link": "https://www.skillshare.com/classes/fiber-optics/189456"},
    ],
    "environmental-engineer": [
        {"title": "Environmental Engineering Principles", "link": "https://www.coursera.org/learn/environmental-engineering"},
        {"title": "Sustainable Urban Development", "link": "https://www.edx.org/course/sustainable-development"},
        {"title": "Wastewater Treatment Basics", "link": "https://www.udemy.com/course/wastewater-treatment"},
        {"title": "Environmental Impact Assessment", "link": "https://www.linkedin.com/learning/environmental-impact-assessment"},
        {"title": "Green Infrastructure and Climate Resilience", "link": "https://www.skillshare.com/classes/green-infrastructure/156345"},
    ],
    "material-science-engineer": [
        {"title": "Materials Science and Engineering Fundamentals", "link": "https://www.coursera.org/learn/materials-science"},
        {"title": "Nanomaterials and Their Applications", "link": "https://www.edx.org/course/nanomaterials-applications"},
        {"title": "Mechanical Properties of Materials", "link": "https://www.udemy.com/course/mechanical-properties"},
        {"title": "Advanced Composites and Alloys", "link": "https://www.linkedin.com/learning/composites-alloys"},
        {"title": "Electronic Properties of Materials", "link": "https://www.skillshare.com/classes/electronic-properties/154786"},
    ],
     "event-manager": [
        {"title": "Event Planning Foundations", "link": "https://www.coursera.org/learn/event-planning"},
        {"title": "Event Management and Design", "link": "https://www.udemy.com/course/event-management"},
        {"title": "Virtual Event Planning Masterclass", "link": "https://www.edx.org/course/virtual-event-planning"},
        {"title": "Budgeting for Events", "link": "https://www.linkedin.com/learning/event-budgeting"},
        {"title": "Event Marketing Strategies", "link": "https://www.skillshare.com/classes/event-marketing/120384"},
    ],
    "cloud-engineer": [
        {
            "title": "AWS Certified Solutions Architect – Associate",
            "link": "https://www.aws.training/Details/Curriculum?id=20685",
        },
        {
            "title": "Google Cloud Professional Cloud Architect",
            "link": "https://cloud.google.com/certification/cloud-architect",
        },
        {
            "title": "Microsoft Azure Fundamentals",
            "link": "https://learn.microsoft.com/en-us/certifications/azure-fundamentals/",
        },
        {
            "title": "Cloud Computing Concepts by UC3M",
            "link": "https://www.coursera.org/learn/cloud-computing-concepts-1",
        },
        {
            "title": "Cloud Engineer Learning Path by LinkedIn",
            "link": "https://www.linkedin.com/learning/paths/become-a-cloud-engineer",
        }
    ],
    "cybersecurity-analyst": [
        {"title": "Introduction to Cybersecurity", "link": "https://www.coursera.org/learn/intro-cybersecurity"},
        {"title": "Cybersecurity Analyst Certification Prep", "link": "https://www.udemy.com/course/cybersecurity-analyst-certification-prep/"},
        {"title": "Foundations of Cybersecurity", "link": "https://www.edx.org/professional-certificate/ibm-cybersecurity-analyst"},
        {"title": "Incident Handling and Response", "link": "https://www.pluralsight.com/courses/incident-handling-response"},
        {"title": "Cyber Threat Intelligence", "link": "https://www.cybrary.it/course/cyber-threat-intelligence/"}
    ],
    "network-engineer": [
        {"title": "Networking Basics", "link": "https://www.coursera.org/learn/networking-basics"},
        {"title": "Cisco CCNA 200-301 Certification Prep", "link": "https://www.udemy.com/course/ccna-complete/"},
        {"title": "Introduction to Network Engineering", "link": "https://www.edx.org/course/introduction-to-network-engineering"},
        {"title": "Networking Concepts and Protocols", "link": "https://www.pluralsight.com/courses/networking-fundamentals"},
        {"title": "Software-Defined Networking", "link": "https://www.linkedin.com/learning/software-defined-networking-sdn/overview"}
    ],
    "hardware-engineer": [
        {"title": "Introduction to Computer Hardware", "link": "https://www.coursera.org/learn/computer-hardware"},
        {"title": "Hardware Design and Architecture", "link": "https://www.udemy.com/course/hardware-design-and-architecture/"},
        {"title": "Computer Organization and Hardware Basics", "link": "https://www.edx.org/course/computer-architecture-and-organization"},
        {"title": "Electronics for Hardware Engineers", "link": "https://www.pluralsight.com/courses/electronics-fundamentals"},
        {"title": "Embedded Hardware Design Fundamentals", "link": "https://www.skillshare.com/classes/embedded-hardware-design/490284"}
    ]
}

@app.route('/learn', methods=['GET'])
def my_learning():
    email = session.get('email')  # Ensure user is logged in
    if not email:
        return redirect('/login')  # Redirect to login if not authenticated

    # Check if career is set in session or database
    career = session.get('career')
    if not career:
        # Fetch career from database if not in session
        student = mongo.db.student.find_one({"email": email})
        if student and "career" in student:
            session['career'] = student['career']  # Update session with career
            career = student['career']
        else:
            return redirect('/career')  # Redirect to career selection if none is set

    # Fetch courses based on career
    if career in career_courses:
        enrolled_courses = career_courses[career]
        return render_template('learn.html', courses=enrolled_courses)
    else:
        return render_template('learn.html', courses=[], message="No courses available.")

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to upload certificate
@app.route('/certificate', methods=['GET', 'POST'])
def upload_certificate():
    if request.method == 'POST':
        course_name = request.form['courseName']
        completion_date = request.form['completionDate']
        certificate_file = request.files['certificateFile']
        email = session.get('email')

        if not email:
            # Handle case when email is not found in the session
            return redirect('/login')  # or show an error message

        if certificate_file and allowed_file(certificate_file.filename):
            filename = secure_filename(certificate_file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)

            # Ensure the uploads folder exists
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)

            # Save the certificate file to the uploads folder
            certificate_file.save(file_path)

            # Save certificate info to MongoDB, appending to the student's record
            mongo.db.student.update_one(
                {"email": email},  # Find the student by email
                {"$push": {  # Using $push to append a new certificate to an array
                    "certificates": {  # Adding a new certificate object inside the array
                        "courseName": course_name,
                        "completionDate": completion_date,
                        "file_url": filename  # Store only the filename, not the full path
                    }
                }},
                upsert=True  # Create a new record if the email doesn't exist
            )

            return redirect('/certificates')  # Redirect to certificates view

    return render_template('certificate.html')

# Route to view certificates
@app.route('/certificates')
def view_certificates():
    email = session.get('email')
    if not email:
        return redirect('/login')

    student = mongo.db.student.find_one({"email": email})

    if student:
        certificates = student.get('certificates', [])
    else:
        certificates = []

    # Generate the correct file URL for each certificate
    for cert in certificates:
        cert['file_url'] = url_for('uploaded_file', filename=cert['file_url'])  # Corrected URL

    return render_template('view_certificates.html', certificates=certificates)


# Serve uploaded files (static files)
@app.route('/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/track', methods=['GET'])
def track_progress():
    email = session.get('email')  # Ensure user email is in session
    if not email:
        return redirect('/login')  # Redirect to login if not authenticated

    # Fetch the career from session
    career = session.get('career')
    if not career or career not in career_courses:
        return redirect('/career')  # Redirect to career selection if not set or invalid

    # Fetch courses for the career
    courses = career_courses.get(career, [])
    
    # Fetch user progress for the selected courses
    student = mongo.db.student.find_one({"email": email})
    progress = student.get('progress', {}) if student else {}

    # Combine course details with progress
    tracked_courses = []
    for course in courses:
        course_title = course['title']
        tracked_courses.append({
            "title": course_title,
            "progress": progress.get(course_title, 0)  # Default progress to 0 if not found
        })

    return render_template('track.html', courses=tracked_courses)


@app.route('/portfolio')
def portfolio():
    email = session.get('email')
    if not email:
        return redirect('/login')

    # Fetch student data
    student = mongo.db.student.find_one({"email": email})
    if not student:
        return "Student not found", 404

    # Process completed courses
    completed_courses = []
    for course in student.get("certificates", []):
        completed_courses.append({
            "course_name": course.get("courseName", "Unnamed Course"),
            "completion_date": course.get("completionDate", "Unknown Date"),
            "file_url": url_for("uploaded_file", filename=course.get("file_url", ""))
        })

    return render_template(
        "portfolio.html",
        student=student,
        completed_courses=completed_courses
    )


if __name__ == '__main__':
    app.run(debug=True)


