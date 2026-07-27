from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_from_directory,
    send_file
)
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os
from werkzeug.utils import secure_filename
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)
app.config.from_object(Config)

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

db = SQLAlchemy(app)


# ------------------------
# DATABASE MODELS
# ------------------------

class Risk(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    risk_name = db.Column(db.String(150), nullable=False)

    owner = db.Column(db.String(100))

    severity = db.Column(db.String(50))

    probability = db.Column(db.String(50))

    impact = db.Column(db.String(50))

    risk_score = db.Column(db.Integer)

    status = db.Column(db.String(50))


class Control(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    control_name = db.Column(db.String(150))
    owner = db.Column(db.String(100))
    status = db.Column(db.String(50))


class Audit(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    audit_name = db.Column(db.String(150))

    auditor = db.Column(db.String(100))

    department = db.Column(db.String(100))

    audit_date = db.Column(db.String(50))

    status = db.Column(db.String(50))

    findings = db.Column(db.String(300))


class Evidence(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(150))

    audit_name = db.Column(db.String(150))

    evidence_type = db.Column(db.String(100))

    upload_date = db.Column(db.String(50))

    description = db.Column(db.String(300))

    file_name = db.Column(db.String(300))


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True, nullable=False)

    password = db.Column(db.String(200), nullable=False)

    role = db.Column(db.String(50))


# ------------------------
# ROUTES
# ------------------------

@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    user = User.query.filter_by(
        username=username,
        password=password
    ).first()

    if user:

        return redirect(url_for("dashboard"))

    return render_template(
        "index.html",
        error="Invalid username or password"
    )

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    total_risks = Risk.query.count()
    open_risks = Risk.query.filter_by(status="Open").count()
    closed_risks = Risk.query.filter_by(status="Closed").count()

    if total_risks == 0:
        compliance_score = 0
    else:
        compliance_score = round((closed_risks / total_risks) * 100)

    critical = Risk.query.filter_by(severity="Critical").count()
    high = Risk.query.filter_by(severity="High").count()
    medium = Risk.query.filter_by(severity="Medium").count()
    low = Risk.query.filter_by(severity="Low").count()
    critical_risks = critical

    total_audits = Audit.query.count()
    ...

    top_risks = (
    Risk.query
    .order_by(Risk.risk_score.desc())
    .limit(5)
    .all()
)

    return render_template(
        "dashboard.html",
        total_risks=total_risks,
        open_risks=open_risks,
        closed_risks=closed_risks,
        critical_risks=critical_risks,
        total_audits=total_audits,
        high=high,
        medium=medium,
        low=low,
        critical=critical,
        top_risks=top_risks,
        compliance_score=compliance_score,
    )

@app.route("/risks")
def risks():

    risks = Risk.query.all()

    return render_template("risks.html", risks=risks)


@app.route("/add-risk", methods=["GET", "POST"])
def add_risk():

    if request.method == "POST":

        score_map = {
            "Low": 1,
            "Medium": 2,
            "High": 3
        }

        risk_score = (
            score_map[request.form["probability"]] *
            score_map[request.form["impact"]]
        )

        risk = Risk(
            risk_name=request.form["risk_name"],
            owner=request.form["owner"],
            severity=request.form["severity"],
            probability=request.form["probability"],
            impact=request.form["impact"],
            risk_score=risk_score,
            status=request.form["status"]
        )

        db.session.add(risk)
        db.session.commit()

        return redirect(url_for("risks"))

    return render_template("add_risk.html")


@app.route("/edit-risk/<int:id>", methods=["GET","POST"])
def edit_risk(id):

    risk = Risk.query.get_or_404(id)

    if request.method == "POST":

        risk.risk_name = request.form["risk_name"]
        risk.owner = request.form["owner"]
        risk.severity = request.form["severity"]
        risk.status = request.form["status"]

        db.session.commit()

        return redirect(url_for("risks"))

    return render_template("edit_risk.html", risk=risk)

@app.route("/delete-risk/<int:id>")
def delete_risk(id):

    print("Trying to delete ID:", id)

    risk = Risk.query.get(id)

    if risk is None:
        return f"Risk with ID {id} not found in database."

    db.session.delete(risk)
    db.session.commit()

    return redirect(url_for("risks"))

@app.route("/controls")
def controls():

    controls = Control.query.all()

    return render_template(
        "controls.html",
        controls=controls
    )


@app.route("/audits")
def audits():

    audits = Audit.query.all()

    return render_template(
        "audits.html",
        audits=audits
    )


@app.route("/evidence")
def evidence():

    evidences = Evidence.query.all()

    return render_template(
        "evidence.html",
        evidences=evidences
    )

@app.route("/add-evidence", methods=["GET", "POST"])
def add_evidence():

    if request.method == "POST":

        file = request.files["file"]

        filename = ""

        if file and file.filename != "":

            filename = secure_filename(file.filename)

            file.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

        evidence = Evidence(

            title=request.form["title"],
            audit_name=request.form["audit_name"],
            evidence_type=request.form["evidence_type"],
            upload_date=request.form["upload_date"],
            description=request.form["description"],
            file_name=filename

        )

        db.session.add(evidence)
        db.session.commit()

        return redirect(url_for("evidence"))

    return render_template("add_evidence.html")

@app.route("/edit-evidence/<int:id>", methods=["GET","POST"])
def edit_evidence(id):

    evidence = Evidence.query.get_or_404(id)

    if request.method=="POST":

        evidence.title = request.form["title"]
        evidence.audit_name = request.form["audit_name"]
        evidence.evidence_type = request.form["evidence_type"]
        evidence.upload_date = request.form["upload_date"]
        evidence.description = request.form["description"]

        db.session.commit()

        return redirect(url_for("evidence"))

    return render_template(
        "edit_evidence.html",
        evidence=evidence
    )

@app.route("/delete-evidence/<int:id>")
def delete_evidence(id):

    evidence = Evidence.query.get_or_404(id)

    db.session.delete(evidence)

    db.session.commit()

    return redirect(url_for("evidence"))


@app.route("/reports")
def reports():

    return render_template("reports.html")

@app.route("/heatmap")
def heatmap():

    risks = Risk.query.all()

    return render_template(
        "heatmap.html",
        risks=risks
    )

@app.route("/add-audit", methods=["GET", "POST"])
def add_audit():

    if request.method == "POST":

        audit = Audit(

            audit_name=request.form["audit_name"],
            auditor=request.form["auditor"],
            department=request.form["department"],
            audit_date=request.form["audit_date"],
            status=request.form["status"],
            findings=request.form["findings"]

        )

        db.session.add(audit)
        db.session.commit()

        return redirect(url_for("audits"))

    return render_template("add_audit.html")

@app.route("/edit-audit/<int:id>", methods=["GET", "POST"])
def edit_audit(id):

    audit = Audit.query.get_or_404(id)

    if request.method == "POST":

        audit.audit_name = request.form["audit_name"]
        audit.auditor = request.form["auditor"]
        audit.department = request.form["department"]
        audit.audit_date = request.form["audit_date"]
        audit.status = request.form["status"]
        audit.findings = request.form["findings"]

        db.session.commit()

        return redirect(url_for("audits"))

    return render_template("edit_audit.html", audit=audit)

@app.route("/delete-audit/<int:id>")
def delete_audit(id):

    audit = Audit.query.get_or_404(id)

    db.session.delete(audit)

    db.session.commit()

    return redirect(url_for("audits"))

@app.route("/uploads/<filename>")
def uploaded_file(filename):

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )

@app.route("/generate-report")
def generate_report():

    pdf_file = "Compliance_Report.pdf"

    doc = SimpleDocTemplate(pdf_file)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph("<b>ComplianceMap Enterprise</b>", styles["Title"])
    )

    elements.append(
        Paragraph("Governance, Risk & Compliance Report", styles["Heading2"])
    )

    elements.append(
        Paragraph("<br/>", styles["Normal"])
    )

    total_risks = Risk.query.count()
    open_risks = Risk.query.filter_by(status="Open").count()
    total_audits = Audit.query.count()
    total_evidence = Evidence.query.count()

    dashboard_data = [

        ["Metric", "Value"],

        ["Total Risks", total_risks],

        ["Open Risks", open_risks],

        ["Audits", total_audits],

        ["Evidence", total_evidence],

        ["Compliance Score", "94%"]

    ]

    dashboard_table = Table(dashboard_data)

    dashboard_table.setStyle(TableStyle([

        ("BACKGROUND",(0,0),(-1,0),colors.darkblue),

        ("TEXTCOLOR",(0,0),(-1,0),colors.white),

        ("GRID",(0,0),(-1,-1),1,colors.black),

        ("BACKGROUND",(0,1),(-1,-1),colors.beige),

        ("BOTTOMPADDING",(0,0),(-1,0),10)

    ]))

    elements.append(dashboard_table)

    elements.append(
        Paragraph("<br/><b>Risk Register</b>", styles["Heading2"])
    )

    risk_data = [["Risk","Severity","Status"]]

    for risk in Risk.query.all():

        risk_data.append([
            risk.risk_name,
            risk.severity,
            risk.status
        ])

    risk_table = Table(risk_data)

    risk_table.setStyle(TableStyle([

        ("BACKGROUND",(0,0),(-1,0),colors.red),

        ("TEXTCOLOR",(0,0),(-1,0),colors.white),

        ("GRID",(0,0),(-1,-1),1,colors.black),

        ("BACKGROUND",(0,1),(-1,-1),colors.whitesmoke)

    ]))

    elements.append(risk_table)

    elements.append(
        Paragraph("<br/><b>Audit Summary</b>", styles["Heading2"])
    )

    audit_data = [["Audit","Status"]]

    for audit in Audit.query.all():

        audit_data.append([
            audit.audit_name,
            audit.status
        ])

    audit_table = Table(audit_data)

    audit_table.setStyle(TableStyle([

        ("BACKGROUND",(0,0),(-1,0),colors.green),

        ("TEXTCOLOR",(0,0),(-1,0),colors.white),

        ("GRID",(0,0),(-1,-1),1,colors.black),

        ("BACKGROUND",(0,1),(-1,-1),colors.beige)

    ]))

    elements.append(audit_table)

    doc.build(elements)

    return send_file(pdf_file, as_attachment=True)



# ------------------------
# MAIN
# ------------------------


if __name__ == "__main__":

    with app.app_context():

        db.create_all()

    app.run(debug=True)