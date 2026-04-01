from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------- MODELS ---------- #

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    skills = db.Column(db.String(200))
    interest = db.Column(db.String(200))

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member1 = db.Column(db.String(100))
    member2 = db.Column(db.String(100))
    member3 = db.Column(db.String(100))
    interest = db.Column(db.String(100))

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(300))

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer)
    title = db.Column(db.String(200))
    status = db.Column(db.String(50))

# ---------- ROLE LOGIC ---------- #

def get_role(skills):
    skills = skills.lower()
    if "python" in skills or "java" in skills:
        return "Developer"
    elif "marketing" in skills or "business" in skills:
        return "Business"
    elif "design" in skills or "ui" in skills:
        return "Designer"
    return "Other"

# ---------- TEAM FORMATION ---------- #

def form_teams(users):
    dev, design, biz = [], [], []

    for u in users:
        role = get_role(u.skills)
        if role == "Developer":
            dev.append(u)
        elif role == "Designer":
            design.append(u)
        elif role == "Business":
            biz.append(u)

    teams = []
    count = min(len(dev), len(design), len(biz))

    for i in range(count):
        teams.append((dev[i], design[i], biz[i]))

    return teams

# ---------- ROUTES ---------- #

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user = User(
            name=request.form['name'],
            skills=request.form['skills'],
            interest=request.form['interest']
        )
        db.session.add(user)
        db.session.commit()
        return redirect('/dashboard')
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    users = User.query.all()
    teams = form_teams(users)
    return render_template('dashboard.html', teams=teams)


@app.route('/save_teams')
def save_teams():
    Team.query.delete()
    db.session.commit()

    users = User.query.all()
    teams = form_teams(users)

    for t in teams:
        db.session.add(Team(
            member1=t[0].name,
            member2=t[1].name,
            member3=t[2].name,
            interest=t[0].interest
        ))

    db.session.commit()
    return redirect('/teams')


@app.route('/teams')
def teams():
    return render_template('teams.html', teams=Team.query.all())


@app.route('/refresh_teams')
def refresh_teams():
    Team.query.delete()
    db.session.commit()
    return redirect('/save_teams')


@app.route('/restart')
def restart():
    db.session.query(User).delete()
    db.session.query(Team).delete()
    db.session.query(Project).delete()
    db.session.query(Task).delete()
    db.session.commit()
    return redirect('/')


# ---------- PROJECT ---------- #

@app.route('/create_project', methods=['GET', 'POST'])
def create_project():
    if request.method == 'POST':
        p = Project(
            name=request.form['name'],
            description=request.form['description']
        )
        db.session.add(p)
        db.session.commit()
        return redirect('/projects')
    return render_template('create_project.html')


@app.route('/projects')
def projects():
    return render_template('projects.html', projects=Project.query.all())


@app.route('/project/<int:id>', methods=['GET', 'POST'])
def project_detail(id):
    project = Project.query.get(id)

    if request.method == 'POST':
        task = Task(
            project_id=id,
            title=request.form['task'],
            status="To Do"
        )
        db.session.add(task)
        db.session.commit()

    tasks = Task.query.filter_by(project_id=id).all()
    return render_template('project_detail.html', project=project, tasks=tasks)


@app.route('/complete_task/<int:id>')
def complete_task(id):
    task = Task.query.get(id)
    task.status = "Done"
    db.session.commit()
    return redirect('/projects')


# ---------- MAIN ---------- #

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)