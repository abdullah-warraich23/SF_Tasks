from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    host = "https://www.softwarefinder.com"
    # Wait time between tasks (1 to 5 seconds)
    wait_time = between(1, 5)

    @task
    def load_test(self):
        # Replace "/" with endpoint if needed
        self.client.get("/")
