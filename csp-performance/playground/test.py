# Import needed libraries

from locust import HttpUser, between, task, TaskSet, SequentialTaskSet

from bs4 import BeautifulSoup


# Set HttpUser class that represents an HTTP “user” which is to be spawned and attacks the system that is to be load
# tested.

class Admin(HttpUser):

    host = 'https://perfcomp.ipa.dataart.net'

    # If test actions re-use another user actions it is possible to describe it in the beginning of the class and
    # then refer to it.

    # Example: all our admin actions work only for logged users. Login has a small probability, so we need to check
    # whether the admin cookie exists or not. And if not, you need to login

    def do_login(self):
        self.client.get("/admin/login", name="Login GET", verify=False)

        self.client.post("/admin/login", data={'login': 'admin',

                                               'password': '0dm1n'},

                         cookies=self.client.cookies.get_dict(),

                         headers={'Content-Type': 'application/x-www-form-urlencoded'},

                         name="Login POST",

                         verify=False)

    def is_logged_in(self):
        if self.client.cookies.get('PHPSESSID') is None:
            self.do_login()

    # task - a convenience decorator to be able to declare tasks inline in the class. number in brackets - weight of
    # task.

    @task(20)
    def login(self):
        print("Login")

        self.do_login()

    # For actions that should be performed one by one we need to use SequentialTaskSet.

    @task(20)
    class searchSet(SequentialTaskSet):

        @task
        def search(self):
            self.parent.is_logged_in()

            self.client.get("/admin/users", cookies=self.client.cookies.get_dict(), name="Search", verify=False)

        @task(2)
        def searchUser(self):
            self.parent.is_logged_in()

            response = self.client.post("/admin/users?q=a", data={'q': 'a'},

                                        cookies=self.client.cookies.get_dict(),

                                        name="Search User",

                                        verify=False)

            soup = BeautifulSoup(response.text, 'html.parser')

            print(soup.find("a"))

        # SequentialTaskSet or other Python loops always need to be stopped with self.interrupt()

        @task(80)
        def stop(self):
            self.interrupt()

    @task(40)
    def profile(self):
        self.is_logged_in()

        self.client.get("/admin",

                        cookies=self.client.cookies.get_dict(),

                        name="Profile",

                        verify=False)
