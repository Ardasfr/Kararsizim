from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from wheels.models import Wheel, WheelOption
from wheels.forms import WheelCreateForm

User = get_user_model()

class WheelTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='carkci_ali',
            email='ali@example.com',
            password='TestPassword123!'
        )
        self.user2 = User.objects.create_user(
            username='carkci_veli',
            email='veli@example.com',
            password='TestPassword123!'
        )

        self.public_wheel = Wheel.objects.create(
            author=self.user1,
            title='Hafta Sonu Ne Yapsak?',
            description='Karar veremedik, çark seçsin!',
            is_public=True
        )
        self.opt1 = WheelOption.objects.create(wheel=self.public_wheel, text='Sinema', order=0)
        self.opt2 = WheelOption.objects.create(wheel=self.public_wheel, text='Piknik', order=1)
        self.opt3 = WheelOption.objects.create(wheel=self.public_wheel, text='Müze', order=2)

        self.private_wheel = Wheel.objects.create(
            author=self.user1,
            title='Gizli Kişisel Karar',
            is_public=False
        )
        WheelOption.objects.create(wheel=self.private_wheel, text='A', order=0)
        WheelOption.objects.create(wheel=self.private_wheel, text='B', order=1)

    def test_wheel_model_and_options(self):
        self.assertEqual(str(self.public_wheel), 'Hafta Sonu Ne Yapsak?')
        self.assertEqual(self.public_wheel.options_count, 3)
        self.assertEqual(self.public_wheel.spin_count, 0)
        self.assertTrue(self.public_wheel.is_public)

    def test_wheel_form_validation(self):
        # 1 seçenek (Hata vermeli - en az 2 olmalı)
        form_few = WheelCreateForm(data={
            'title': 'Test Çark',
            'choices[]': ['Yalnızca Bir']
        })
        self.assertFalse(form_few.is_valid())

        # 3 seçenek (Geçerli olmalı)
        form_valid = WheelCreateForm(data={
            'title': 'Test Çark',
            'choices[]': ['Pizza', 'Burger', 'Makarna'],
            'is_public': True
        })
        self.assertTrue(form_valid.is_valid())
        self.assertEqual(len(form_valid.cleaned_data['cleaned_choices']), 3)

        # 21 seçenek (Hata vermeli - en fazla 20 olmalı)
        too_many = [f'Secenek {i}' for i in range(21)]
        form_too_many = WheelCreateForm(data={
            'title': 'Test Çark',
            'choices[]': too_many
        })
        self.assertFalse(form_too_many.is_valid())

    def test_authenticated_user_can_create_wheel(self):
        self.client.login(username='carkci_ali', password='TestPassword123!')
        create_url = reverse('wheels:create')

        response = self.client.post(create_url, {
            'title': 'Akşam Yemeği Menüsü',
            'description': 'Lezzetli bir seçim',
            'is_public': 'on',
            'choices[]': ['Köfte', 'Pide', 'Mantı']
        })

        self.assertEqual(response.status_code, 302)
        new_wheel = Wheel.objects.filter(title='Akşam Yemeği Menüsü').first()
        self.assertIsNotNone(new_wheel)
        self.assertEqual(new_wheel.author, self.user1)
        self.assertTrue(new_wheel.is_public)
        self.assertEqual(new_wheel.options.count(), 3)

    def test_anonymous_user_cannot_create_wheel(self):
        # Anonim kullanıcı çark oluşturma sayfasına gittiğinde login'e yönlendirilmeli
        create_url = reverse('wheels:create')
        get_resp = self.client.get(create_url)
        self.assertEqual(get_resp.status_code, 302)
        self.assertIn('/accounts/login/', get_resp.url)

        post_resp = self.client.post(create_url, {
            'title': 'İzinsiz Çark',
            'choices[]': ['A', 'B']
        })
        self.assertEqual(post_resp.status_code, 302)
        self.assertFalse(Wheel.objects.filter(title='İzinsiz Çark').exists())

    def test_anonymous_user_can_view_and_spin_public_wheel(self):
        # Anonim kullanıcı paylaşılan çark detayına erişebilmeli
        detail_url = reverse('wheels:detail', kwargs={'wheel_id': self.public_wheel.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hafta Sonu Ne Yapsak?')
        self.assertContains(response, 'Sinema')
        self.assertContains(response, 'Piknik')
        self.assertContains(response, 'Müze')

        # Anonim kullanıcı çevirme sayacı isteği atabilmeli
        spin_url = reverse('wheels:spin_record', kwargs={'wheel_id': self.public_wheel.id})
        spin_resp = self.client.post(spin_url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(spin_resp.status_code, 200)
        data = spin_resp.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['spin_count'], 1)

        self.public_wheel.refresh_from_db()
        self.assertEqual(self.public_wheel.spin_count, 1)

    def test_private_wheel_access_restrictions(self):
        # Gizli çark: Anonim kullanıcı 404 almalı
        detail_url = reverse('wheels:detail', kwargs={'wheel_id': self.private_wheel.id})
        anon_resp = self.client.get(detail_url)
        self.assertEqual(anon_resp.status_code, 404)

        # Başka bir giriş yapmış kullanıcı (user2) da 404 almalı
        self.client.login(username='carkci_veli', password='TestPassword123!')
        other_user_resp = self.client.get(detail_url)
        self.assertEqual(other_user_resp.status_code, 404)

        # Çarkın sahibi (user1) görüntüleyebilmeli
        self.client.login(username='carkci_ali', password='TestPassword123!')
        owner_resp = self.client.get(detail_url)
        self.assertEqual(owner_resp.status_code, 200)
        self.assertContains(owner_resp, 'Gizli Kişisel Karar')

    def test_wheel_deletion_permissions(self):
        # User2 çarkı silmeye çalışırsa 403 Forbidden almalı
        delete_url = reverse('wheels:delete', kwargs={'wheel_id': self.public_wheel.id})
        self.client.login(username='carkci_veli', password='TestPassword123!')
        forbidden_resp = self.client.post(delete_url)
        self.assertEqual(forbidden_resp.status_code, 403)
        self.assertTrue(Wheel.objects.filter(id=self.public_wheel.id).exists())

        # Çarkın sahibi (user1) silerse başarılı olmalı
        self.client.login(username='carkci_ali', password='TestPassword123!')
        delete_resp = self.client.post(delete_url)
        self.assertEqual(delete_resp.status_code, 302)
        self.assertFalse(Wheel.objects.filter(id=self.public_wheel.id).exists())

    def test_wheel_list_feed_and_search(self):
        list_url = reverse('wheels:list')
        resp = self.client.get(list_url)
        self.assertEqual(resp.status_code, 200)
        # Herkese açık çark akışta görünmeli
        self.assertIn(self.public_wheel, resp.context['wheels'])
        # Gizli çark akışta görünmemeli
        self.assertNotIn(self.private_wheel, resp.context['wheels'])

        # Arama testi
        search_found = self.client.get(list_url, {'q': 'Hafta Sonu'})
        self.assertIn(self.public_wheel, search_found.context['wheels'])

        search_not_found = self.client.get(list_url, {'q': 'BulunmayacakKelimexyz'})
        self.assertNotIn(self.public_wheel, search_not_found.context['wheels'])
