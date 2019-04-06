from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Company, CompanyUser, Log
from datetime import datetime


class CompanyTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        '''Wire Up defaults'''
        cls.company = Company.objects.create(name='default')

    def test_company_was_created_correctly(self):
        '''Check if one company was inserted in DB as expected'''
        self.assertEqual(1, Company.objects.count())
        self.assertEqual(self.company.name, Company.objects.get(name='default').name)


class CompanyUserTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        '''Wire Up defaults'''
        cls.company = Company.objects.create(name='default')
        Company.objects.create(id=2, name='Company 2')

    def setUp(self):
        pass

    def test_should_create_a_user_form_company_2(self):
        CompanyUser.create(user_id=1, username='zero dois', email='zero@dois.org', password='test', company_id=2).save()
        self.assertEqual('Company 2', User.objects.get(pk=1).companyuser.company.name)


class LogTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        '''Wire Up defaults'''
        # Set up Companies
        cls.company = Company.objects.create(id=1, name='default')
        Company.objects.create(id=2, name='Company 2')
        Company.objects.create(id=3, name='Company 3')
        # Set up users
        # A bulk_create wouldnt work with overriden save method
        CompanyUser.create(user_id=1, username='test', email='test@test.org', password='test', company_id=1).save()
        CompanyUser.create(user_id=2, username='zero dois', email='zero@dois.org', password='test', company_id=2).save()
        CompanyUser.create(user_id=3, username='zero tres', email='zero@tres.org', password='test', company_id=3).save()
        CompanyUser.create(user_id=4, username='zero quatro', email='zero@quatro.org', password='test',
                           company_id=3).save()
        CompanyUser.create(user_id=5, username='zero cinco', email='zero@cinco.org', password='test',
                           company_id=3).save()
        CompanyUser.create(user_id=10, username='zero dez', email='zero@dez.org', password='test', company_id=1).save()

        # Set up logs
        Log.objects.bulk_create([
            # user_id, company_id, event_name, action, date_time
            # 1, 1, login, put, 2019 - 04 - 01 11: 03:50
            Log.create(user_id=1, company_id=1, event_name='login', action='put',
                       date_time=datetime.strptime('2019-04-01 11:03:50', '%Y-%m-%d %H:%M:%S')),
            # 2, 2, budget, put, 2019 - 04 - 02 12: 03:50
            Log.create(user_id=2, company_id=2, event_name='budget', action='put',
                       date_time=datetime.strptime('2019-04-02 12:03:50', '%Y-%m-%d %H:%M:%S')),
            # 3, 3, dashboard, get, 2019 - 04 - 01 11: 05:50
            Log.create(user_id=3, company_id=3, event_name='dashboard', action='get',
                       date_time=datetime.strptime('2019-04-01 11:05:50', '%Y-%m-%d %H:%M:%S')),
            # 4, 3, dashboard, get, 2019 - 04 - 01 11: 07:50
            Log.create(user_id=4, company_id=3, event_name='dashboard', action='get',
                       date_time=datetime.strptime('2019-04-01 11:07:50', '%Y-%m-%d %H:%M:%S')),
            # 4, 3, budget, get, 2019 - 04 - 01 11: 05:50
            Log.create(user_id=4, company_id=3, event_name='budget', action='get',
                       date_time=datetime.strptime('2019-04-01 11:05:50', '%Y-%m-%d %H:%M:%S')),
            # 5, 3, budget, put, 2019 - 04 - 01 11: 10:50
            Log.create(user_id=5, company_id=3, event_name='budget', action='put',
                       date_time=datetime.strptime('2019-04-01 11:05:50', '%Y-%m-%d %H:%M:%S')),
            # 5, 3, login, put, 2019 - 01 - 01 11: 10:50
            Log.create(user_id=5, company_id=3, event_name='login', action='put',
                       date_time=datetime.strptime('2019-01-01 11:05:50', '%Y-%m-%d %H:%M:%S')),
            # 10, 1, dashboard, get, 2019 - 04 - 01 12: 05:50
            Log.create(user_id=10, company_id=1, event_name='dashboard', action='get',
                       date_time=datetime.strptime('2019-04-01 12:05:50', '%Y-%m-%d %H:%M:%S')),
        ])

    def test_should_have_tree_companies(self):
        self.assertEqual(3, Company.objects.count())

    def test_should_have_six_users(self):
        self.assertEqual(6, User.objects.count())

    def test_should_print_first_log_entry_when_pk_1_is_given(self):
        log = Log.objects.get(pk=1)
        self.assertEqual('[Log Entry : login - put - 2019-04-01 11:03:50 - test - default]', log.__str__())

    def test_should_raise_exception_when_user_doesnt_exist(self):
        with(self.assertRaises(User.DoesNotExist)):
            Log.create(user_id=6, company_id=1, event_name='login', action='put')

    def test_should_raise_exception_when_company_doesnt_exist(self):
        with(self.assertRaises(self.company.DoesNotExist)):
            Log.create(user_id=1, company_id=5, event_name='login', action='put')

    def test_should_return_two_log_entry_for_company_default(self):
        result = Company.objects.get(pk=1).get_last_20_days_actions()
        self.assertEqual(2, len(result))

    def test_should_return_four_log_entries_for_company_tree(self):
        result = Company.objects.get(pk=3).get_last_20_days_actions()
        self.assertEqual(4, len(result))

    def test_should_raise_exception_for_non_existing_company(self):
        with(self.assertRaises(self.company.DoesNotExist)):
            Company.objects.get(pk=6).get_last_20_days_actions()

    def test_should_return_user_zero_cinco_as_whom_executed_more_actions(self):
        result = Log.get_most_active_user()
        self.assertEqual(5, result['user'])

    def test_should_return_dashboard_as_the_most_accessed_event(self):
        result = Log.get_most_accessed_event()
        self.assertEqual('dashboard', result['event_name'])

    def test_should_return_budget_as_the_single_event_for_company_2(self):
        result = Company.objects.select_related().get(pk=2).get_all_events_for_company()
        self.assertEqual(1, len(result))
        self.assertTrue(result.filter(event_name='budget').exists())

    def test_should_return_budget_and_dashboard_for_company_3(self):
        result = Company.objects.get(pk=3).get_all_events_for_company()
        self.assertEqual(5, len(result))
        self.assertTrue(result.filter(event_name='budget').exists())
        self.assertTrue(result.filter(event_name='dashboard').exists())

    def test_should_return_all_events_for_company_3(self):
        result = Company.objects.get(pk=3).get_last_20_days_actions()
        self.assertEqual(4, len(result))
        self.assertTrue(result.filter(event_name='budget').exists())
        self.assertTrue(result.filter(event_name='dashboard').exists())
