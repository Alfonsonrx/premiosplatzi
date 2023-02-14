import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls.base import reverse

from .models import Question
# Create your tests here.
class QuestionModelTests(TestCase):
    
    def setUp(self):
        """
        Setting the question model to use on each test
        """
        self.question = Question(question_text="Quien es el mejor director?")
    
    def test_was_recently_published_with_future_questions(self):
        """
        With a future question on list
        the function was_published_recently has to return False
        """
        time = timezone.now() + datetime.timedelta(days=30)
        self.question.pub_date = time
        self.assertFalse(self.question.was_published_recently())
        
    def test_was_published_recently_present_questions(self):
        """
        With a question published now, the function must return True
        """
        self.question.pub_date=timezone.now()
        self.assertTrue(self.question.was_published_recently())
        
    def test_was_published_recently_past_questions(self):
        """
        Having a question published 30 days ago, the function must return False
        """
        time = timezone.now() - datetime.timedelta(days=30)
        self.question.pub_date = time
        self.assertFalse(self.question.was_published_recently())

def create_question(question_text, days):
    """
    Creating a new question and setting different time for the test on views
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)
    
class QuestionViewTests(TestCase):

    def test_not_questions(self):
        """
        No questions on the context, displaying no polls available 
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context["latest_question_list"], [])
        
    def test_was_recently_published_past(self):
        """
        Questions with pub_date before now are displayed on index
        """
        question = create_question("Quien es el mejor alumno?", days=-15)
        # time = timezone.now() - datetime.timedelta(days=15)
        # Question.objects.create(question_text="Quien es el mejor alumno?", pub_date=time)
        response = self.client.get(reverse('polls:index'))
        q_list = response.context["latest_question_list"]
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(q_list, [question])
        for q in q_list:
            self.assertEqual(q.pub_date > timezone.now(), False)
        
    def test_was_recently_published_future(self):
        """
        Questions with future pub_date will not be displayed
        """
        create_question("Quien es el mejor alumno?", days=15)
        # time = timezone.now() + datetime.timedelta(days=15)
        # Question.objects.create(question_text="Quien es el mejor alumno?", pub_date = time)
        
        response = self.client.get(reverse('polls:index'))
        q_list = response.context["latest_question_list"]
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(q_list, [])
        
        for q in q_list:
            self.assertEqual(q.pub_date > timezone.now(), False)
        
    def test_future_and_past_questions(self):
        """
        Two questions with future and past pub_date, only past will be displayed
        """
        create_question('future question', days=10)
        questionp = create_question('past question', days=-10)
        response = self.client.get(reverse('polls:index'))
        q_list = response.context["latest_question_list"]
        
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(q_list, [questionp])

        for q in q_list:
            self.assertEqual(q.pub_date > timezone.now(), False)
        
    def test_two_past_questions(self):
        """
        Two past questions, both will be displayed on index view
        """
        questionp1 = create_question('past question', days=-5)
        questionp2 = create_question('past question', days=-10)
        
        response = self.client.get(reverse('polls:index'))
        q_list = response.context["latest_question_list"]
        
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(q_list, [questionp1, questionp2])

        for q in q_list:
            self.assertEqual(q.pub_date > timezone.now(), False)
    
class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view from a question with a future pub_date must return 404 error not found
        """
        future_question = create_question('future question', days=30)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_past_question(self):
        """
        The detail view from a question with a past pub_date must display the question's text
        """
        past_question = create_question('past question', days=-30)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)