import requests
import time
import os

URL = "http://" + os.environ.get("HOST", "") + ":" + str(os.environ.get("PORT", ""))

methods = {
    'GET' : requests.get,
    'POST' : requests.post,
    'PATCH' : requests.patch
}

def print_request(method, endpoint, payload = {}):
    print "REQUEST:", method
    print URL + endpoint
    print payload
    print
    START = time.time()
    resp = methods[method](URL + endpoint, json = payload)
    TIME = time.time() - START
    print "RESPONSE:", resp.status_code
    print "Received in %f s" % TIME
    print resp.text
    print '____________________________________________________________'
    print
    return resp, TIME


if  __name__ == '__main__':
    timeout = int(os.environ.get("WAITDB", "120"))

    while True:

        try:

            resp, _ = print_request("GET", "/dbcheck")

            if resp.status_code != 200:
                if timeout <= 0:
                    raise Exception("DB not working =(")
                time.sleep(5.0)
                timeout -= 5
            else:
                break
        except Exception as e:
            if timeout <= 0:
                raise Exception("Something not working:", e.message)
            time.sleep(5.0)
            timeout -= 5
