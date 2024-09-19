from locust import HttpUser, task, events, tag, TaskSet, SequentialTaskSet
import logging
from http.client import HTTPConnection
import urllib3
import shortuuid

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# HTTPConnection.debuglevel = 1
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


@task(10)
class Public(HttpUser):
    # The class defines a wait_time that will make the simulated users wait between 1 and 5 seconds after each task
    # wait_time = between(1, 5)
    host = 'http://perfcomp.ipa.dataart.net'
    weight = 10
    @task(85)
    def get_homepage(self):
        self.client.get("/login",
                        name="Homepage",
                        verify=False,
                        )

    @task(10)
    def registration(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
        }
        self.client.post(f"/registration?login=ERNESTEST_REG_{shortuuid.uuid()}&password=123",
                         name="Registration",
                         headers=headers,
                         verify=False,
                         )

    @task
    class ForgotPassword(TaskSet):

        @task(5)
        def forgot_password(self):
            payload = 'email=test%2540dataart.com'
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Content-Length': '34',
                'Content-Type': 'application/x-www-form-urlencoded',
                'DNT': '1',
                'Upgrade-Insecure-Requests': '1',
            }
            self.client.post("/forgot",
                             name="Forgot",
                             data=payload,
                             headers=headers,
                             verify=False,
                             )
