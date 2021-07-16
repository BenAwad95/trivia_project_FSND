import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import true   
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}@{}/{}".format(
                                                            'postgres:Ruba2334',
                                                            'localhost:5432',
                                                            self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        # create new question for test
        self.question_test = Question(question="How are you",
                                      answer="Fine, thanks",
                                      difficulty=5, category='sport')
        self.question_test.insert()
        # create new category for test
        self.category_test = Category(type="Sport")
        self.category_test.insert()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for/
    expected errors.
    """
    # test for GET '/categories'
    # ------------------------
    def test_get_all_categories(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['categories']) # not empty.

    def test_post_categories(self):
        response = self.client().post('/questions')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['massage'], 'Unprocessable!')
        self.assertFalse(data['success']) 
    # ------------------------
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
        self.assertEqual(data['massage'], 'Resource Not Found')
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
        response = self.client().delete('/questions/5000')
        
        self.assertEqual(response.status_code, 404)
    # ------------------------
    # test for POST '/questions'
    # ------------------------
    
    def test_create_question(self):
        response = self.client().post('/questions',
                                      json={
                                            'question': 'question',
                                            'answer': 'answer',
                                            'difficulty': 10,
                                            'category': 'sport'
                                            }, content_type='application/json')
        data = json.loads(response.data)
        # print(data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_filed_create_question(self):
        response = self.client().post('/questions',
                                      json={
                                            'qus': 'question',
                                            'answer': 'answer',
                                            'difficulty': 'not integer',
                                            'category': 'sport'
                                            }, content_type='application/json')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['massage'], 'Unprocessable!')
        self.assertEqual(data['error'], 422)
# ------------------------
# test for search questions
# ------------------------

    def test_search_questions(self):
        response = self.client().post('/questions/search', json={'searchTerm': 'a'})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['questions'])

    def test_search_without_questions(self):
        response = self.client().post('/questions/search', json={'searchTerm': 'some random search term'})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['totalQuestions'], 0)
# ------------------------
# test for get questions of category
# ------------------------

    def test_get_category_questions(self):
        response = self.client().get(f'/categories/{self.category_test.id}/questions')
        data = json.loads(response.data)
        ca_questions = [q.format() for q in Question.query.filter_by(category = f"{self.category_test.id}").all()]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['questions'], ca_questions)
    
    def test_get_unfounded_category_questions(self):
        response = self.client().get('/categories/1000/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])
# ------------------------
# test for quiz question
# ------------------------

    def test_get_one_question(self):
        response = self.client().post('/quizzes', json={'previous_questions':[], 'quiz_category':{'id': 0, 'type': 'all'}})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['question']), 5)  # five columns

    def test_post_quiz_without_json(self):
        response = self.client().post('/quizzes', json={})
        data = json.loads(response.data)

        self.assertEqual(data['error'], 400)        
        self.assertEqual(data['massage'], 'Bad Request!')        
        self.assertFalse(data['success'])  
      
# Make the tests conveniently executable


if __name__ == "__main__":
    unittest.main()