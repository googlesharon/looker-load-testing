from realbrowserlocusts import HeadlessChromeLocust
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from locust import TaskSet, task, between
import configparser


SITE = "https://jcp-dev.lookersandbox.com"
DASH_ID = 8


class LocustUserBehavior(TaskSet):

    def on_start(self):
        self.login()

    def on_stop(self):
        self.logout()

    def login(self):
        self.client.get(SITE + "/login")
        user_entry, pass_entry = parse_website_creds(SITE.partition("//")[2])

        username = self.client.find_element_by_id("login-email")
        pw = self.client.find_element_by_id("login-password")
        username.clear()
        username.send_keys(user_entry)
        pw.clear()
        pw.send_keys(pass_entry)
        self.client.find_element_by_id("login-submit").click()

    def logout(self):
        print("stopping session")

    def open_dashboard(self):

        script = """
        setTimeout(function() {
            document.addEventListener('dashboard.rendered', function() {
                var dash_render = document.createElement("div");
                dash_render.id = "dash_listener";
                document.body.appendChild(dash_render);
            }, false);
        }, 500);"""

        try:
            self.client.get(f"{SITE}/embed/dashboards/{str(DASH_ID)}")
            self.client.execute_script(script)
            self.client.wait.until(
                EC.presence_of_element_located(
                    (By.ID, "dash_listener")
                )
            )
        except TimeoutException:
            print("hit timeout")

    @task(1)
    def simple_dashboard_loading(self):
        self.client.timed_event_for_locust(
            "Load", "dashboard",
            self.open_dashboard
        )


class LocustUser(HeadlessChromeLocust):

    host = "dashboard load test"
    timeout = 5  # in seconds in waitUntil thingies
    wait_time = between(1, 2)
    screen_width = 1200
    screen_height = 600
    task_set = LocustUserBehavior


def parse_website_creds(site, ini="looker.ini"):
    config = configparser.ConfigParser()
    config.read(ini)
    web_creds = config[site]
    return (web_creds["username"], web_creds["password"])
