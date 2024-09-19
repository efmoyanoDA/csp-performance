from random import randrange

from locust import HttpUser, task, events, tag, TaskSet, SequentialTaskSet
import logging
import shortuuid
from bs4 import BeautifulSoup
from http.client import HTTPConnection
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# HTTPConnection.debuglevel = 1
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


@task(5)
class Admin(HttpUser):
    # The class defines a wait_time that will make the simulated users wait between 1 and 5 seconds after each task
    # wait_time = between(1, 5)
    host = 'https://perfcomp.ipa.dataart.net'
    weight = 5

    profile_id = 0

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
        self.client.get("/admin/login",
                        name="Login GET",
                        verify=False
                        )

        with self.client.post("/admin/login", data={'login': 'admin', 'password': '0dm1n'},
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

    def login(self):
        self.exec_login()

    @task(20)
    class SearchSet(SequentialTaskSet):

        @task
        def search(self):
            self.parent.exec_login()
            payload = 'q=ERNESTEST'
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            }

            with self.parent.client.post("/admin/users",
                                         headers=headers,
                                         data=payload,
                                         verify=False,
                                         name="Search User",
                                         catch_response=True
                                         ) as response:
                # Get random profile ID
                soup = BeautifulSoup(response.text, 'html.parser')
                ids = soup.select('input[name="id"]')
                self.parent.profile_id = ids[randrange(len(ids))]['value']

        @task
        class UserSet(TaskSet):

            @task(30)
            def add_user(self):
                self.parent.parent.is_logged_in()
                payload = f'login=ERNESTEST_{shortuuid.uuid()}&password=123'
                headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Cache-Control': 'max-age=0',
                    'Connection': 'keep-alive',
                    'Content-Length': '30',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'DNT': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-User': '?1',
                    'Upgrade-Insecure-Requests': '1',
                    'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"macOS"',
                }

                self.client.post("/admin/add_user",
                                 data=payload,
                                 headers=headers,
                                 name="Add User",
                                 verify=False,
                                 catch_response=True
                                 )

            @task(234)
            def search_user(self):
                self.parent.parent.is_logged_in()
                payload = 'q=ERNESTEST'
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                }

                self.parent.client.post("/admin/users",
                                        headers=headers,
                                        data=payload,
                                        verify=False,
                                        name="Search User",
                                        catch_response=True
                                        )

            @task(25)
            def block_user(self):
                payload = f'id={self.parent.parent.profile_id}'
                headers = {
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Content-Length': '7',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'DNT': '1',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin',
                    'X-Requested-With': 'XMLHttpRequest',
                    'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"macOS"'
                }

                self.parent.client.post("/admin/block",
                                        headers=headers,
                                        data=payload,
                                        verify=False,
                                        name="Block User",
                                        )

            @task(15)
            def delete_user(self):
                payload = f'id={self.parent.parent.profile_id}'
                headers = {
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Content-Length': '7',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'DNT': '1',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
                    'X-Requested-With': 'XMLHttpRequest',
                    'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"macOS"',
                }

                with self.parent.client.post("/admin/delete",
                                             headers=headers,
                                             data=payload,
                                             verify=False,
                                             name="Delete User",
                                             catch_response=True
                                             ) as response:
                    if response.text == "":
                        response.failure(f"Failed to delete {self.parent.parent.profile_id} user")
                    if response.status_code == 200:
                        response.success()
                    print(response.text)

    @task(2)
    class Settings(TaskSet):

        @task(5)
        def save_settings(self):
            self.parent.exec_login()
            payload = 'email_change=1&user%255Blogin%255D=admin&user%255Bemail%255D=admin%2540admin.com'
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Content-Length': '70',
                'Content-Type': 'application/x-www-form-urlencoded',
                'DNT': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
            }

            with self.parent.client.post("/admin",
                                         headers=headers,
                                         data=payload,
                                         verify=False,
                                         name="Settings - Save",
                                         catch_response=True
                                         ) as response:
                # Get random profile ID
                soup = BeautifulSoup(response.text, 'html.parser')
                message = soup.find("div", class_="error").get_text()
                if message == "Changes were applied.":
                    response.success()
                else:
                    response.failure(f"Failed to save settings")

        @task(20)
        def change_password(self):
            self.parent.exec_login()
            payload = 'email_change=1&user%255Blogin%255D=admin&user%255Bemail%255D=admin%2540admin.com'
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Content-Length': '70',
                'Content-Type': 'application/x-www-form-urlencoded',
                'DNT': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
            }

            with self.parent.client.post("/admin",
                                         headers=headers,
                                         data=payload,
                                         verify=False,
                                         name="Settings - Change password",
                                         catch_response=True
                                         ) as response:
                # Get random profile ID
                soup = BeautifulSoup(response.text, 'html.parser')
                message = soup.find("div", class_="error").get_text()
                if message == "Changes were applied.":
                    response.success()
                else:
                    response.failure(f"Failed to save settings")

    @task(33)
    def get_logs(self):
        self.is_logged_in()
        payload = 'from_date=2023-02-09&to_date=2023-02-10'
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Content-Length': '39',
            'Content-Type': 'application/x-www-form-urlencoded',
            'DNT': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }
        self.client.post("/admin/logs",
                         headers=headers,
                         data=payload,
                         verify=False,
                         name="Logs - Search logs",
                         catch_response=True
                         )

    @task(25)
    class Complaints(TaskSet):

        complaint_id = 0

        @task(75)
        def search_complaint(self):
            self.parent.exec_login()
            payload = 'from_date=2023-02-09&to_date=2023-02-10'
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Content-Length': '39',
                'Content-Type': 'application/x-www-form-urlencoded',
                'DNT': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
                'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
            }

            with self.parent.client.post("/admin/complaints",
                                         headers=headers,
                                         data=payload,
                                         verify=False,
                                         name="Complaints - Search",
                                         catch_response=True
                                         ) as response:
                # Get random profile ID
                soup = BeautifulSoup(response.text, 'html.parser')
                complaint_list = soup.find_all("input", class_="delete_complaint")
                self.complaint_id = complaint_list[randrange(len(complaint_list))]['data-id']

        @task(15)
        def delete_complaint(self):
            self.parent.exec_login()
            headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive',
                'DNT': '1',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest',
                'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
            }

            self.parent.client.post(f"/admin/complaints/delete?id={self.complaint_id}",
                                    headers=headers,
                                    verify=False,
                                    name="Complaints - Delete",
                                    catch_response=True
                                    )
