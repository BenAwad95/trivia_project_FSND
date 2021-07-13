import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
   
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}@{}/{}".format('postgres:Ruba2334' ,'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
        
        # create new question for test
        self.question_test = Question(question="How are you", answer="Fine, thanks", difficulty=5,category='sport')
        self.question_test.insert()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # test for GET '/questions'
    # ------------------------
    def test_get_paginated_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
    
    def test_404_empty_page(self):
        response = self.client().get('/questions/?page1000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['massage'], 'Response Not Found')
    # ------------------------
    # test for DELETE '/questions/<question_id>'
    # ------------------------
    def test_delete_question(self):
        response = self.client().delete(f'/questions/{self.question_test.id}')
        # data = json.loads(response.data)

        # print(data)
        deleted_question = Question.query.filter(Question.id == self.question_test.id).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(deleted_question, None)
    
    def test_delete_none_question(self):
        response = self.client().delete(f'/questions/5000')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 404)
    # ------------------------
    # test for POST '/questions'
    # ------------------------
    def test_create_question(self):
        response = self.client().post(f'/questions',
        json={
            'question':'question',
            'answer':'answer',
            'difficulty':10,
            'category':'sport'
            }, content_type='application/json')
        data = json.loads(response.data)
        # print(data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
    
    def test_filed_create_question(self):
        response = self.client().post(f'/questions',
        json={
            'qus':'question',
            'answer':'answer',
            'difficulty':'not integer',
            'category':'sport'
            }, content_type='application/json')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['massage'], 'Unprocessable!')
        self.assertEqual(data['error'], 422)
# ------------------------
# test for get questions of category
# ------------------------
    def test_get_category_questions(self):
        CATEGORY = Category.query.get(1)
        response = self.client().get(f'/categories/{CATEGORY.id}/questions')
        data = json.loads(response.data)
        ca_questions = [q.format() for q in Question.query.filter(Question.category.ilike(CATEGORY.type))]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['questions'], ca_questions)
# ------------------------
# ---
# ------------------------


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()