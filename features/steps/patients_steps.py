from behave import given, when, then
import requests
import subprocess
import time

CONTAINER_NAME = "dicomweb-proxy-test"


def start_container():
    subprocess.run(["docker", "build", "-t", CONTAINER_NAME, "."], check=True)
    proc = subprocess.Popen(["docker", "run", "-d", "-p", "8000:8000", "--name", CONTAINER_NAME, CONTAINER_NAME])
    time.sleep(5)
    return proc


def stop_container():
    subprocess.run(["docker", "stop", CONTAINER_NAME], check=False)
    subprocess.run(["docker", "rm", CONTAINER_NAME], check=False)


@given("the dicomweb proxy is running in Docker")
def given_running_proxy(context):
    context.proc = start_container()


@when('I request "{path}"')
def when_request(context, path):
    context.response = requests.get(f"http://localhost:8000{path}")


@then("the response code should be 200")
def then_status(context):
    assert context.response.status_code == 200
    stop_container()

