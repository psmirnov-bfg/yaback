import requests

from test import URL
from random_test import generate_random_citizen

def test_bad():

    citizen = generate_random_citizen(1)
    citizen["name"] = 1111
    resp = requests.post(URL + '/imports', json={"citizens":[citizen]})
    assert resp.status_code == 400

    citizen = generate_random_citizen(1)
    citizen["relatives"] = ["abra"]
    resp = requests.post(URL + '/imports', json={"citizens": [citizen]})
    assert resp.status_code == 400

    citizen = generate_random_citizen(1)
    citizen["relatives"] = 666
    resp = requests.post(URL + '/imports', json={"citizens": [citizen]})
    assert resp.status_code == 400

    citizen = generate_random_citizen(1)
    citizen["name"] = ''
    resp = requests.post(URL + '/imports', json={"citizens": [citizen]})
    assert resp.status_code == 400

    citizen = generate_random_citizen(1)
    citizen["birth_date"] = '31.02.2019'
    resp = requests.post(URL + '/imports', json={"citizens": [citizen]})
    assert resp.status_code == 400

    citizen = generate_random_citizen(1)
    citizen["gender"] = 'human'
    resp = requests.post(URL + '/imports', json={"citizens": [citizen]})
    assert resp.status_code == 400

    citizen = generate_random_citizen(1)
    citizen["building"] = '{{{}}}'
    resp = requests.post(URL + '/imports', json={"citizens": [citizen]})
    assert resp.status_code == 400

    citizens = [generate_random_citizen(x) for x in range(3)]
    citizens[0]["relatives"] = [1, "abra"]
    citizens[1]["relatives"] = 0
    resp = requests.post(URL + '/imports', json={"citizens": citizens})
    assert resp.status_code == 400

    citizens = [generate_random_citizen(x) for x in range(3)]
    citizens[0]["relatives"] = [1, 2]
    resp = requests.post(URL + '/imports', json={"citizens": citizens})
    assert resp.status_code == 400

    citizens = [generate_random_citizen(x) for x in range(3)]
    citizens[0]["relatives"] = [1, 1, 2, 2]
    citizens[1]["relatives"] = [0]
    citizens[2]["relatives"] = [0]
    resp = requests.post(URL + '/imports', json={"citizens": citizens})
    assert resp.status_code == 400

    citizens = [generate_random_citizen(x) for x in range(3)]
    resp = requests.post(URL + '/imports', json={"citizens": citizens})
    assert resp.status_code == 200
    import_id = resp.json()["data"]["import_id"]

    resp = requests.patch(URL + '/imports/%d/citizens/%d' % (import_id, 1), json = {
        "name" : ''
    })
    assert resp.status_code == 400

    resp = requests.patch(URL + '/imports/%d/citizens/%d' % (import_id, 1), json={
        "birth_date": '31.02.2019'
    })
    assert resp.status_code == 400

    resp = requests.patch(URL + '/imports/%d/citizens/%d' % (import_id, 1), json={
        "relatives": [0,1,1,0]
    })
    assert resp.status_code == 400

    resp = requests.patch(URL + '/imports/%d/citizens/%d' % (import_id, 1), json={
        "relatives": [5]
    })
    assert resp.status_code == 400

    resp = requests.patch(URL + '/imports/%d/citizens/%d' % (import_id, 1), json={
        "relatives": ['cadabra']
    })
    assert resp.status_code == 400

    resp = requests.patch(URL + '/imports/%d/citizens/%d' % (import_id, 666), json={
        "name": 'newcitizen'
    })
    assert resp.status_code == 400
