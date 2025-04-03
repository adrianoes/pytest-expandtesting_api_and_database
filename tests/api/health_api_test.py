import requests

def test_check_health_api():
    resp = requests.get("https://practice.expandtesting.com/notes/api/health-check")
    print(resp)
    assert True == resp.json()['success']
    assert 200 == resp.json()['status']
    assert "Notes API is Running" == resp.json()['message']


