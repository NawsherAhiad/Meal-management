import unittest
import os
import sys
from datetime import date, datetime, timedelta
from flask import Flask
from flask_testing import TestCase

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Member, MealRecord

class TestMealManagement(TestCase):
    """Unit tests for Meal Management System"""
    
    def create_app(self):
        """Create Flask app for testing"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = 'test-secret-key'
        app.config['ADMIN_PASSWORD'] = 'test-admin'
        app.config['WTF_CSRF_ENABLED'] = False
        return app
    
    def setUp(self):
        """Set up test database"""
        db.create_all()
    
    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
    
    def test_index_redirects(self):
        """Test that index redirects to add_member"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/add-member', response.location)
    
    def test_add_member_page_loads(self):
        """Test add member page loads correctly"""
        response = self.client.get('/add-member')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Add New Member', response.data)
        self.assertIn(b'Banasree Boys', response.data)
    
    def test_add_member_success(self):
        """Test adding a new member"""
        response = self.client.post('/add-member', data={
            'name': 'John Doe'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Check member was added to database
        member = Member.query.filter_by(name='John Doe').first()
        self.assertIsNotNone(member)
        self.assertEqual(member.name, 'John Doe')
    
    def test_add_duplicate_member(self):
        """Test adding duplicate member fails"""
        # Add first member
        member1 = Member(name='John Doe')
        db.session.add(member1)
        db.session.commit()
        
        # Try to add duplicate
        response = self.client.post('/add-member', data={
            'name': 'John Doe'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'already exists', response.data)
    
    def test_add_empty_member_name(self):
        """Test adding member with empty name fails"""
        response = self.client.post('/add-member', data={
            'name': ''
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'valid name', response.data)
    
    def test_meals_page_loads(self):
        """Test meals page loads correctly"""
        response = self.client.get('/meals')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Today\'s Meal Tracking', response.data)
        self.assertIn(b'Banasree Boys', response.data)
    
    def test_meals_page_with_members(self):
        """Test meals page shows members"""
        # Add a member
        member = Member(name='John Doe')
        db.session.add(member)
        db.session.commit()
        
        response = self.client.get('/meals')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'John Doe', response.data)
    
    def test_save_meal_record(self):
        """Test saving meal record for today"""
        # Add a member
        member = Member(name='John Doe')
        db.session.add(member)
        db.session.commit()
        
        today = date.today()
        today_str = today.strftime('%Y-%m-%d')
        
        # Save meal record
        response = self.client.post('/meals', data={
            f'meal_count_{today_str}_{member.id}': '3'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'successfully', response.data)
        
        # Check record was saved
        record = MealRecord.query.filter_by(
            member_id=member.id,
            meal_date=today
        ).first()
        self.assertIsNotNone(record)
        self.assertEqual(record.meal_count, 3)
    
    def test_update_existing_meal_record(self):
        """Test updating existing meal record"""
        # Add member and record
        member = Member(name='John Doe')
        db.session.add(member)
        db.session.commit()
        
        today = date.today()
        record = MealRecord(
            member_id=member.id,
            meal_date=today,
            meal_count=2
        )
        db.session.add(record)
        db.session.commit()
        
        today_str = today.strftime('%Y-%m-%d')
        
        # Update meal record
        response = self.client.post('/meals', data={
            f'meal_count_{today_str}_{member.id}': '4'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Check record was updated
        record = MealRecord.query.filter_by(
            member_id=member.id,
            meal_date=today
        ).first()
        self.assertEqual(record.meal_count, 4)
    
    def test_export_pdf(self):
        """Test PDF export functionality"""
        # Add member and meal records
        member = Member(name='John Doe')
        db.session.add(member)
        db.session.commit()
        
        today = date.today()
        record = MealRecord(
            member_id=member.id,
            meal_date=today,
            meal_count=3
        )
        db.session.add(record)
        db.session.commit()
        
        response = self.client.get('/export-pdf')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/pdf')
        self.assertIn(b'%PDF', response.data[:4])  # PDF magic number
    
    def test_admin_login_page_loads(self):
        """Test admin login page loads"""
        response = self.client.get('/admin')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Admin Login', response.data)
    
    def test_admin_login_success(self):
        """Test successful admin login"""
        response = self.client.post('/admin', data={
            'password': 'test-admin'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Admin Panel', response.data)
    
    def test_admin_login_failure(self):
        """Test failed admin login"""
        response = self.client.post('/admin', data={
            'password': 'wrong-password'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid password', response.data)
    
    def test_admin_add_member(self):
        """Test admin can add member"""
        # Login as admin
        with self.client.session_transaction() as sess:
            sess['admin_logged_in'] = True
        
        response = self.client.post('/admin', data={
            'add_member': '1',
            'member_name': 'Admin Added Member'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Check member was added
        member = Member.query.filter_by(name='Admin Added Member').first()
        self.assertIsNotNone(member)
    
    def test_admin_remove_member(self):
        """Test admin can remove member"""
        # Add a member
        member = Member(name='To Be Removed')
        db.session.add(member)
        db.session.commit()
        member_id = member.id
        
        # Login as admin
        with self.client.session_transaction() as sess:
            sess['admin_logged_in'] = True
        
        # Remove member
        response = self.client.post('/admin', data={
            'remove_member': '1',
            'member_id': str(member_id)
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Check member was removed
        member = Member.query.get(member_id)
        self.assertIsNone(member)
    
    def test_admin_edit_meal_record(self):
        """Test admin can edit meal record"""
        # Add member and record
        member = Member(name='John Doe')
        db.session.add(member)
        db.session.commit()
        
        today = date.today()
        record = MealRecord(
            member_id=member.id,
            meal_date=today,
            meal_count=2
        )
        db.session.add(record)
        db.session.commit()
        record_id = record.id
        
        # Login as admin
        with self.client.session_transaction() as sess:
            sess['admin_logged_in'] = True
        
        # Edit meal record
        response = self.client.post('/admin', data={
            'update_meal': '1',
            'record_id': str(record_id),
            'member_id': str(member.id),
            'meal_date': today.strftime('%Y-%m-%d'),
            'meal_count': '4'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Check record was updated
        record = MealRecord.query.get(record_id)
        self.assertEqual(record.meal_count, 4)
    
    def test_meal_count_range_0_to_4(self):
        """Test meal count dropdown only has 0-4 options"""
        # Add a member first
        member = Member(name='Test Member')
        db.session.add(member)
        db.session.commit()
        
        response = self.client.get('/meals')
        self.assertEqual(response.status_code, 200)
        
        # Check that 5 is not in the options
        self.assertNotIn(b'<option value="5"', response.data)
        # Check that 0-4 are present
        self.assertIn(b'<option value="0"', response.data)
        self.assertIn(b'<option value="4"', response.data)

if __name__ == '__main__':
    unittest.main()
