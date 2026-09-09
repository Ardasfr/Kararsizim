from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from polls.models import Poll, Choice, Vote
from polls.forms import PollCreateForm

User = get_user_model()

class KararsizimTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='denemeuser',
            email='deneme@example.com',
            password='TestPassword123!'
        )
        self.poll = Poll.objects.create(
            author=self.user1,
            question='Hangi telefonu tercih edersin?'
        )
        self.c1 = Choice.objects.create(poll=self.poll, text='iPhone 16 Pro', order=0)
        self.c2 = Choice.objects.create(poll=self.poll, text='Samsung S24 Ultra', order=1)

    def test_custom_user_creation(self):
        self.assertEqual(self.user1.username, 'denemeuser')
        self.assertEqual(self.user1.email, 'deneme@example.com')
        self.assertTrue(self.user1.check_password('TestPassword123!'))

    def test_poll_and_choices(self):
        self.assertEqual(self.poll.choices.count(), 2)
        self.assertEqual(self.poll.total_votes, 0)

    def test_poll_form_validation_min_max(self):
        # 1 seçenek (Hata vermeli - en az 2 olmalı)
        form_invalid = PollCreateForm(data={
            'question': 'Tek seçenekli soru',
            'choices[]': ['Tek seçenek']
        })
        self.assertFalse(form_invalid.is_valid())

        # 3 seçenek (Geçerli olmalı)
        form_valid = PollCreateForm(data={
            'question': 'Geçerli soru',
            'choices[]': ['A', 'B', 'C']
        })
        self.assertTrue(form_valid.is_valid())

        # 6 seçenek (Hata vermeli - en fazla 5 olmalı)
        form_too_many = PollCreateForm(data={
            'question': 'Çok seçenek',
            'choices[]': ['A', 'B', 'C', 'D', 'E', 'F']
        })
        self.assertFalse(form_too_many.is_valid())

    def test_anonymous_voting_and_results_visibility(self):
        # 1. Oy vermeden sonuçlar sayfasına gitmeyi dene -> redirect olmalı
        results_url = reverse('polls:results', kwargs={'poll_id': self.poll.id})
        response = self.client.get(results_url)
        self.assertEqual(response.status_code, 302)  # Detaya yönlendirir

        # 2. Anonim olarak oy ver
        vote_url = reverse('polls:vote', kwargs={'poll_id': self.poll.id})
        vote_response = self.client.post(vote_url, {'choice': str(self.c1.id)})
        self.assertEqual(vote_response.status_code, 302)

        # 3. Veritabanında oy oluştu mu kontrol et
        self.assertEqual(self.poll.total_votes, 1)
        self.assertEqual(self.c1.vote_count, 1)
        self.assertEqual(self.c2.vote_count, 0)
        self.assertEqual(self.c1.percentage(), 100.0)

        # 4. Artık oy verildiğine göre sonuçlar sayfasına erişilebilmeli
        response_after = self.client.get(results_url)
        self.assertEqual(response_after.status_code, 200)
        self.assertContains(response_after, 'iPhone 16 Pro')
        self.assertContains(response_after, '100')

        # 5. Aynı anonim session ile tekrar oy vermeyi dene -> Çift oy engeli!
        duplicate_vote = self.client.post(vote_url, {'choice': str(self.c2.id)})
        self.assertEqual(self.poll.total_votes, 1)  # Oy sayısı artmamalı

    def test_ajax_voting(self):
        vote_url = reverse('polls:vote', kwargs={'poll_id': self.poll.id})
        ajax_resp = self.client.post(
            vote_url,
            {'choice': str(self.c2.id)},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(ajax_resp.status_code, 200)
        data = ajax_resp.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['total_votes'], 1)
        self.assertEqual(data['voted_choice_id'], str(self.c2.id))
