from random import randrange

from locust import HttpUser, task, events, tag, TaskSet
import names
import logging
from bs4 import BeautifulSoup
from http.client import HTTPConnection

# This was very useful to debug the issue with avatar upload
# HTTPConnection.debuglevel = 1
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

@task(85)
class User(HttpUser):
    # The class defines a wait_time that will make the simulated users wait between 1 and 5 seconds after each task
    # wait_time = between(1, 5)
    host = 'http://perfcomp.ipa.dataart.net'
    weight = 85

    test_user_id = 2500
    perf_user_id = 2499

    @events.test_start.add_listener
    def on_test_start(environment, **kwargs):
        print("----------------------")
        print("A new test is starting")
        print("----------------------")

    @events.test_stop.add_listener
    def on_test_stop(environment, **kwargs):
        print("----------------------")
        print("A new test is ending")
        print("----------------------")

    def on_start(self):
        print("on_start")

    def on_stop(self):
        print("on_stop")

    def exec_login(self):
        self.client.get("/login",
                        name="Login GET",
                        verify=False
                        )

        with self.client.post("/login", data={'login': 'ernestest_DA', 'password': '123'},
                              headers={'Content-Type': 'application/x-www-form-urlencoded'},
                              cookies=self.client.cookies.get_dict(),
                              name="Login POST",
                              verify=False,
                              catch_response=True
                              ) as response:
            if response.text == "":
                response.failure("Got wrong response")
            elif response.elapsed.total_seconds() > 0.5:
                response.failure("Request took too long")
            if response.status_code == 200:
                response.success()

    def is_logged_in(self):
        if self.client.cookies.get("PHPSESSID") is None:
            self.exec_login()

    @task(10)
    def login(self):
        self.exec_login()

    @task(33)
    class ProfileSet(TaskSet):

        @task(140)
        def get_profile(self):
            self.client.get("/profile",
                            name="Get Profile",
                            verify=False
                            )

        @task(3)
        def upload_avatar(self):
            self.parent.is_logged_in()
            payload = {'upload': ''}
            files = [
                ('image', ('bender.png', open('resources/bender.png', 'rb'),
                           'image/png'))
            ]

            self.client.post("/profile/avatar",
                             data=payload,
                             files=files,
                             name="Upload Avatar",
                             verify=False)

        @task(5)
        def rate_user(self):
            payload = f'val=4.71&votes=5&user_id={self.parent.test_user_id}&score=4.6'
            headers = {
                'Connection': 'keep-alive',
                'Content-Length': '37',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
            }
            self.client.post("/profile/rate",
                             data=payload,
                             cookies=self.client.cookies.get_dict(),
                             headers=headers,
                             name="Rate User",
                             verify=False)

        @task(20)
        def edit_profile(self):
            self.client.post("/profile/edit",
                             data=f"profile%5Bfirstname%5D={names.get_first_name()}&profile%5Bmiddlename%5D={names.get_first_name()}&profile%5Blastname%5D=Moyano&profile%5BDOB%5D=2023-02-01&profile%5Bcountry%5D=&profile%5Bsex%5D=0&profile%5Binterests%5D=dev&profile%5Bphone%5D=092023",
                             cookies=self.client.cookies.get_dict(),
                             headers={'Content-Type': 'application/x-www-form-urlencoded'},
                             name="Edit Profile",
                             verify=False)

        @task(5)
        def compliant_user(self):
            self.client.post("/profile/complaint",
                             data=f"complaint%5Bsuspect%5D={self.parent.test_user_id}&complaint%5Breason%5D=test+from+ernesto+to+bender",
                             cookies=self.client.cookies.get_dict(),
                             headers={'Content-Type': 'application/x-www-form-urlencoded',
                                      'X-Requested-With': "XMLHttpRequest"},
                             name="Compliant User",
                             verify=False)

        @task(30)
        def send_wall_message(self):
            self.parent.is_logged_in()
            payload = {'id': self.parent.test_user_id,
                       'message': 'Test Wall Message'}
            files = [
                ('image', ('bender.png', open('resources/bender.png', 'rb'),
                           'image/png'))
            ]

            self.client.post("/profile/wall",
                             files=files,
                             data=payload,
                             cookies=self.client.cookies.get_dict(),
                             name="Send Wall Message",
                             verify=False)

    @task(20)
    class SearchSet(TaskSet):
        @task(90)
        def search_user(self):
            self.parent.is_logged_in()
            with self.client.get("/search?q=a",
                                 name="Search User",
                                 verify=False,
                                 catch_response=True
                                 ) as response:
                soup = BeautifulSoup(response.text, 'html.parser')
                ids = soup.select('input[name="id"]')
                # print(ids[randrange(len(ids))]['value'])

    @task(35)
    class MessageSet(TaskSet):
        @task(150)
        def get_user_list(self):
            self.parent.is_logged_in()
            headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'X-Requested-With': 'XMLHttpRequest'
            }
            self.client.get("/users?term=a",
                            name="Get Users List",
                            headers=headers,
                            verify=False,
                            )

        @task(50)
        def get_message_history(self):
            self.parent.is_logged_in()
            headers = {
                'Accept': 'text/html, */*; q=0.01',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive',
                'DNT': '1',
                'X-Requested-With': 'XMLHttpRequest'
            }
            self.client.get(f"/message/history?to_id={self.parent.test_user_id}&from_id={self.parent.perf_user_id}",
                            name="Get Message History",
                            headers=headers,
                            verify=False,
                            catch_response=True
                            )

        @task(70)
        def send_message(self):
            self.parent.is_logged_in()
            headers = {
                'Accept': 'text/html, */*; q=0.01',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive',
                'DNT': '1',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            self.client.post("/message/add",
                             name="Send New Message",
                             data=f"to_id={self.parent.test_user_id}&from_id={self.parent.perf_user_id}&message%5Bto%5D=Bender+John+Futurama&message%5Bheader%5D=HEADER+1+LOCUST&message%5Bbody%5D=BODY+1+LOCUST",
                             headers=headers,
                             verify=False,
                             )

    @task(2)
    class SettingsSet(TaskSet):
        @task(30)
        def update_email(self):
            self.parent.is_logged_in()
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Content-Length': '110',
                'Content-Type': 'application/x-www-form-urlencoded',
                'DNT': '1',
                'Upgrade-Insecure-Requests': '1',
            }
            self.client.post("/settings",
                             name="Settings - Update Email",
                             data=f"email_change=1&user%5Blogin%5D=ernesto&user%5Bemail%5D=dernesto.LOCUST.moyano%40dataart.com",
                             headers=headers,
                             verify=False,
                             )

        @task(10)
        def update_password(self):
            self.parent.is_logged_in()
            payload = 'change_password=1&user%255Bpassword%255D=123&user%255Bpassword_new_1%255D=123&user%255Bpassword_new_2%255D=123'
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Content-Length': '98',
                'Content-Type': 'application/x-www-form-urlencoded',
                'DNT': '1',
                'Upgrade-Insecure-Requests': '1',
            }
            self.client.post("/settings",
                             name="Settings - Update Password",
                             data=payload,
                             headers=headers,
                             verify=False,
                             )

    @task
    class PlaygroundSet(TaskSet):
        @tag('playground')
        @task(10)
        def not_found_get(self):
            with self.client.get("/does_not_exist/", name="Not found GET", catch_response=True) as response:
                if response.status_code == 404:
                    response.success()

        @tag('playground')
        @task(10)
        def not_found_post(self):
            with self.client.post("/does_not_exist/", name="Not found POST", catch_response=True) as response:
                if response.status_code == 404:
                    response.success()
