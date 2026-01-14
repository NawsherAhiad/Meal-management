from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
# Support both PostgreSQL and SQLite (for local testing)
database_url = os.getenv('DATABASE_URL')
if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Fallback to SQLite for local testing
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meal_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['ADMIN_PASSWORD'] = os.getenv('ADMIN_PASSWORD', 'admin123')

db = SQLAlchemy(app)

# Database Models
class Member(db.Model):
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MealRecord(db.Model):
    __tablename__ = 'meal_records'
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    meal_date = db.Column(db.Date, nullable=False)
    meal_count = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    member = db.relationship('Member', backref=db.backref('meal_records', lazy=True))
    
    __table_args__ = (db.UniqueConstraint('member_id', 'meal_date', name='unique_member_date'),)

# Routes
@app.route('/')
def index():
    return redirect(url_for('add_member'))

@app.route('/add-member', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if name:
            # Check if member already exists
            existing_member = Member.query.filter_by(name=name).first()
            if existing_member:
                flash('Member already exists!', 'error')
            else:
                new_member = Member(name=name)
                db.session.add(new_member)
                db.session.commit()
                flash(f'Member "{name}" added successfully!', 'success')
                return redirect(url_for('add_member'))
        else:
            flash('Please enter a valid name!', 'error')
    
    members = Member.query.order_by(Member.name).all()
    return render_template('add_member.html', members=members)

@app.route('/meals', methods=['GET', 'POST'])
def meals():
    today = date.today()
    today_str = today.strftime('%Y-%m-%d')
    
    if request.method == 'POST':
        # Get all members
        members = Member.query.order_by(Member.name).all()
        
        # Process form data for today only
        for member in members:
            meal_count_key = f'meal_count_{today_str}_{member.id}'
            meal_count = request.form.get(meal_count_key)
            
            if meal_count is not None:
                try:
                    meal_count = int(meal_count)
                    # Get or create meal record for today
                    meal_record = MealRecord.query.filter_by(
                        member_id=member.id,
                        meal_date=today
                    ).first()
                    
                    if meal_record:
                        meal_record.meal_count = meal_count
                        meal_record.updated_at = datetime.utcnow()
                    else:
                        meal_record = MealRecord(
                            member_id=member.id,
                            meal_date=today,
                            meal_count=meal_count
                        )
                        db.session.add(meal_record)
                except ValueError:
                    continue
        
        db.session.commit()
        flash('Today\'s meal records updated successfully!', 'success')
        return redirect(url_for('meals'))
    
    # Get all members
    members = Member.query.order_by(Member.name).all()
    
    # Get today's meal records
    today_records = MealRecord.query.filter_by(meal_date=today).all()
    today_meals = {record.member_id: record.meal_count for record in today_records}
    
    return render_template('meals.html', members=members, today_meals=today_meals, today=today, today_str=today_str)

@app.route('/export-pdf')
def export_pdf():
    # Get current month
    today = date.today()
    start_date = date(today.year, today.month, 1)
    
    # Calculate end date (last day of current month)
    if today.month == 12:
        end_date = date(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(today.year, today.month + 1, 1) - timedelta(days=1)
    
    # Get all members
    members = Member.query.order_by(Member.name).all()
    
    # Get all meal records for current month
    meal_records = MealRecord.query.filter(
        MealRecord.meal_date >= start_date,
        MealRecord.meal_date <= end_date
    ).all()
    
    # Calculate totals for each member
    member_totals = {}
    for record in meal_records:
        if record.member_id not in member_totals:
            member_totals[record.member_id] = 0
        member_totals[record.member_id] += record.meal_count
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=20,
        alignment=TA_LEFT
    )
    
    # Title
    story.append(Paragraph("Banasree Boys", title_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"Monthly Meal Report - {today.strftime('%B %Y')}", heading_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Table data
    table_data = [['Member Name', 'Total Meals']]
    
    for member in members:
        total = member_totals.get(member.id, 0)
        table_data.append([member.name, str(total)])
    
    # Create table
    table = Table(table_data, colWidths=[4*inch, 2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 0.3*inch))
    
    # Total summary
    grand_total = sum(member_totals.values())
    story.append(Paragraph(f"<b>Grand Total: {grand_total} meals</b>", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, textColor=colors.grey)))
    
    doc.build(story)
    buffer.seek(0)
    
    filename = f"meal_report_{today.strftime('%Y_%m')}.pdf"
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name=filename)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # Check if admin is logged in
    if not session.get('admin_logged_in'):
        if request.method == 'POST':
            password = request.form.get('password', '')
            if password == app.config['ADMIN_PASSWORD']:
                session['admin_logged_in'] = True
                flash('Admin login successful!', 'success')
                return redirect(url_for('admin'))
            else:
                flash('Invalid password!', 'error')
        return render_template('admin_login.html')
    
    # Admin is logged in
    if request.method == 'POST':
        # Handle logout
        if 'logout' in request.form:
            session.pop('admin_logged_in', None)
            flash('Logged out successfully!', 'success')
            return redirect(url_for('admin'))
        
        # Handle add member
        if 'add_member' in request.form:
            member_name = request.form.get('member_name', '').strip()
            if member_name:
                existing_member = Member.query.filter_by(name=member_name).first()
                if existing_member:
                    flash(f'Member "{member_name}" already exists!', 'error')
                else:
                    new_member = Member(name=member_name)
                    db.session.add(new_member)
                    db.session.commit()
                    flash(f'Member "{member_name}" added successfully!', 'success')
            else:
                flash('Please enter a valid member name!', 'error')
            return redirect(url_for('admin'))
        
        # Handle remove member
        if 'remove_member' in request.form:
            member_id = request.form.get('member_id')
            if member_id:
                try:
                    member = Member.query.get(member_id)
                    if member:
                        member_name = member.name
                        # Delete all meal records for this member
                        MealRecord.query.filter_by(member_id=member_id).delete()
                        # Delete the member
                        db.session.delete(member)
                        db.session.commit()
                        flash(f'Member "{member_name}" and all their meal records removed successfully!', 'success')
                    else:
                        flash('Member not found!', 'error')
                except Exception as e:
                    flash(f'Error removing member: {str(e)}', 'error')
                    db.session.rollback()
            return redirect(url_for('admin'))
        
        # Handle meal record update
        if 'update_meal' in request.form:
            record_id = request.form.get('record_id')
            new_count = request.form.get('meal_count')
            meal_date = request.form.get('meal_date')
            member_id = request.form.get('member_id')
            
            try:
                new_count = int(new_count)
                meal_date = datetime.strptime(meal_date, '%Y-%m-%d').date()
                
                if record_id:
                    # Update existing record
                    record = MealRecord.query.get(record_id)
                    if record:
                        record.meal_count = new_count
                        record.updated_at = datetime.utcnow()
                        db.session.commit()
                        flash('Meal record updated successfully!', 'success')
                else:
                    # Create new record
                    existing = MealRecord.query.filter_by(
                        member_id=member_id,
                        meal_date=meal_date
                    ).first()
                    
                    if existing:
                        existing.meal_count = new_count
                        existing.updated_at = datetime.utcnow()
                    else:
                        new_record = MealRecord(
                            member_id=member_id,
                            meal_date=meal_date,
                            meal_count=new_count
                        )
                        db.session.add(new_record)
                    
                    db.session.commit()
                    flash('Meal record saved successfully!', 'success')
            except Exception as e:
                flash(f'Error updating record: {str(e)}', 'error')
            
            return redirect(url_for('admin'))
    
    # Get date range for viewing (default: last 30 days)
    days_back = int(request.args.get('days', 30))
    start_date = date.today() - timedelta(days=days_back)
    end_date = date.today()
    
    # Get all members
    members = Member.query.order_by(Member.name).all()
    
    # Get meal records in date range
    meal_records = MealRecord.query.join(Member).filter(
        MealRecord.meal_date >= start_date,
        MealRecord.meal_date <= end_date
    ).order_by(MealRecord.meal_date.desc(), Member.name).all()
    
    # Group records by date
    records_by_date = {}
    for record in meal_records:
        date_str = record.meal_date.strftime('%Y-%m-%d')
        if date_str not in records_by_date:
            records_by_date[date_str] = []
        records_by_date[date_str].append(record)
    
    return render_template('admin.html', 
                         members=members, 
                         records_by_date=records_by_date,
                         days_back=days_back,
                         start_date=start_date,
                         end_date=end_date)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Only run in debug mode if explicitly set
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
