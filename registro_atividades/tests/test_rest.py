from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from registro_atividades.models import Company
from datetime import datetime


class CompanyTest(APITestCase):
    @classmethod
    def __format_user_dict(cls, user_id, first_name, last_name, password, company_id):
        dic = {"user": {"id": user_id, "is_superuser": False, "username": f'{first_name}{last_name}', "first_name": first_name,
                        "last_name": last_name, "password": password, "is_staff": False, "is_active": True,
                        "email": f'{first_name}@{last_name}.org'}, "company": company_id}
        return dic

    @classmethod
    def __post_json(cls, url, data):
        client = APIClient()
        return client.post(url, data, format='json')

    @classmethod
    def __format_log_dict(cls, event_name, action, date_time, user_id, company_id):
        dic = {"event_name": event_name, "action": action, "date_time": date_time, "user": user_id,
               "company": company_id}

        return dic

    @classmethod
    def __check_status(cls, data, url):
        response = cls.__post_json(url, data)
        print(response.data)

    @classmethod
    def setUpTestData(cls):
        client = APIClient()
        # companies
        print('Creating Companies')
        cls.company_url = reverse('company-list')
        data = {'name': 'default'}
        cls.response_first = client.post(cls.company_url, data, format='json')
        [cls.__post_json(cls.company_url, {'id': index + 2, 'name': name}) for index, name in
         enumerate(('Company 2', 'Company 3'), 0)]

        # users
        print('Creating Users')
        cls.user_url = reverse('companyuser-list')
        [cls.__check_status(data, cls.user_url) for data in
         (cls.__format_user_dict(user_id=1, first_name='test', last_name='test', password='test', company_id=1),
          cls.__format_user_dict(user_id=2, first_name='zero', last_name='dois', password='test', company_id=2),
          cls.__format_user_dict(user_id=3, first_name='zero', last_name='tres', password='test', company_id=3),
          cls.__format_user_dict(user_id=4, first_name='zero', last_name='quatro', password='test', company_id=3),
          cls.__format_user_dict(user_id=5, first_name='zero', last_name='cinco', password='test', company_id=3),
          cls.__format_user_dict(user_id=6, first_name='zero', last_name='dez', password='test', company_id=1),
          )]

        # Logs
        print('Creating Logs')
        cls.log_url = reverse('log-list')
        [cls.__check_status(data, cls.log_url) for data in (
            # user_id, company_id, event_name, action, date_time
            # 1, 1, login, put, 2019 - 04 - 01 11: 03:50
            cls.__format_log_dict(user_id=1, company_id=1, event_name='login', action='put',
                                  date_time=datetime.strptime('2019-04-01 11:03:50', '%Y-%m-%d %H:%M:%S')),
            # 2, 2, budget, put, 2019 - 04 - 02 12: 03:50
            cls.__format_log_dict(user_id=2, company_id=2, event_name='budget', action='put',
                                  date_time=datetime.strptime('2019-04-02 12:03:50', '%Y-%m-%d %H:%M:%S')),
            # 3, 3, dashboard, get, 2019 - 04 - 01 11: 05:50
            cls.__format_log_dict(user_id=3, company_id=3, event_name='dashboard', action='get',
                                  date_time=datetime.strptime('2019-04-01 11:05:50', '%Y-%m-%d %H:%M:%S')),
            # 4, 3, dashboard, get, 2019 - 04 - 01 11: 07:50
            cls.__format_log_dict(user_id=4, company_id=3, event_name='dashboard', action='get',
                                  date_time=datetime.strptime('2019-04-01 11:07:50', '%Y-%m-%d %H:%M:%S')),
            # 4, 3, budget, get, 2019 - 04 - 01 11: 05:50
            cls.__format_log_dict(user_id=4, company_id=3, event_name='budget', action='get',
                                  date_time=datetime.strptime('2019-04-01 11:05:50', '%Y-%m-%d %H:%M:%S')),
            # 5, 3, budget, put, 2019 - 04 - 01 11: 10:50
            cls.__format_log_dict(user_id=5, company_id=3, event_name='budget', action='put',
                                  date_time=datetime.strptime('2019-04-01 11:05:50', '%Y-%m-%d %H:%M:%S')),
            # 5, 3, login, put, 2019 - 01 - 01 11: 10:50
            cls.__format_log_dict(user_id=5, company_id=3, event_name='login', action='put',
                                  date_time=datetime.strptime('2019-01-01 11:05:50', '%Y-%m-%d %H:%M:%S')),
            # 10, 1, dashboard, get, 2019 - 04 - 01 12: 05:50
            cls.__format_log_dict(user_id=6, company_id=1, event_name='dashboard', action='get',
                                  date_time=datetime.strptime('2019-04-01 12:05:50', '%Y-%m-%d %H:%M:%S')),
        )]

    def test_post_company(self):
        self.assertEqual(self.response_first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Company.objects.count(), 3)
        self.assertEqual(Company.objects.get(name=self.response_first.json()['name']).name, 'default')

    def test_should_have_tree_companies_inserted(self):
        response = self.client.get(self.company_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(3, len(response.json()))

    def test_should_have_six_users_inserted(self):
        response = self.client.get(self.user_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(6, len(response.json()))

    def test_should_raise_exception_for_non_existing_company(self):
        response = self.client.get(f'{self.company_url}8/actions')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # def test_should_return_four_log_entries_for_company_tree(self):
    #     response = self.client.get(f'{self.company_url}3/actions')
    #      self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     print(response.data)
    #
    # def test_should_return_user_zero_cinco_as_whom_executed_more_actions(self):
    #     result = Log.get_most_active_user()
    #     self.assertEqual(5, result['user'])
    #
    # def test_should_return_dashboard_as_the_most_accessed_event(self):
    #     result = Log.get_most_accessed_event()
    #     self.assertEqual('dashboard', result['event_name'])
    #
    # def test_should_return_budget_as_the_single_event_for_company_2(self):
    #     result = Company.objects.select_related().get(pk=2).get_all_events_for_company()
    #     self.assertEqual(1, len(result))
    #     self.assertTrue(result.filter(event_name='budget').exists())
    #
    # def test_should_return_budget_and_dashboard_for_company_3(self):
    #     result = Company.objects.get(pk=3).get_all_events_for_company()
    #     self.assertEqual(5, len(result))
    #     self.assertTrue(result.filter(event_name='budget').exists())
    #     self.assertTrue(result.filter(event_name='dashboard').exists())
    #
    # def test_should_return_all_events_for_company_3(self):
    #     result = Company.objects.get(pk=3).get_last_20_days_actions()
    #     self.assertEqual(4, len(result))
    #     self.assertTrue(result.filter(event_name='budget').exists())
    #     self.assertTrue(result.filter(event_name='dashboard').exists())
