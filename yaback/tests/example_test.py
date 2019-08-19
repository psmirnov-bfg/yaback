# coding=utf-8
import pytest
import random
from test import print_request

def test_example():

    resp, _ = print_request("POST", "/imports", {
        "citizens": [
            {
                "citizen_id": 1,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "name": "Иванов Иван Иванович",
                "birth_date": "26.12.%d" % random.choice(range(1900,2018)),
                "gender": "male",
                "relatives": [2]
            },
            {
                "citizen_id": 2,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "name": "Иванов Сергей Иванович",
                "birth_date": "17.04.%d" % random.choice(range(1900,2018)),
                "gender": "male",
                "relatives": [1]
            },
            {
                "citizen_id": 3,
                "town": "Керчь",
                "street": "Иосифа Бродского",
                "building": "2",
                "apartment": 11,
                "name": "Романова Мария Леонидовна",
                "birth_date": "23.11.%d" % random.choice(range(1900,2018)),
                "gender": "female",
                "relatives": []
            }

        ]
    })

    assert (resp.status_code == 200)

    tmp, _ = print_request("GET", "/imports/%d/citizens" % resp.json()["data"]["import_id"])

    assert (tmp.status_code == 200)
    assert (len(tmp.json()["data"]) == 3)

    tmp, _  = print_request("GET", "/imports/%d/towns/stat/percentile/age" % resp.json()["data"]["import_id"])

    assert (tmp.status_code == 200)

    tmp2 = [x for x in tmp.json()["data"] if x["town"] == u'Керчь'][0]
    assert (tmp2["p50"] == tmp2["p75"] == tmp2["p99"])

    tmp = [x for x in tmp.json()["data"] if x["town"] == u'Москва'][0]

    # Linear percentile for 2 numbers reversion
    young = 3 * tmp["p50"] - 2 * tmp["p75"]
    old = 2 * tmp["p75"] - tmp["p50"]

    q99 = 0.99 * old + 0.01 * young

    assert (abs(tmp["p99"] - q99) < 0.001)

    tmp, _ = print_request("PATCH", "/imports/%d/citizens/3" % resp.json()["data"]["import_id"], {
        "name": "Иванова' WHERE id = 1; DROP TABLE relatives; UPDATE citizens SET name = 'Мария Леонидовна",
        "town": "Москва",
        "street": "Льва Толстого",
        "building": "16к7стр5",
        "apartment": 7,
        "relatives": [1],
        "gender" : "male"
    })

    assert (tmp.status_code == 200)
    assert (str(tmp.json()["data"]["relatives"]) == '[1]')

    tmp, _ = print_request("GET", "/imports/%d/citizens" % resp.json()["data"]["import_id"])
    assert (tmp.status_code == 200)
    tmp = tmp.json()["data"]
    assert (str(sorted([x for x in tmp if x["citizen_id"] == 1][0]["relatives"]) == '[2, 3]'))
    assert (str(sorted([x for x in tmp if x["citizen_id"] == 2][0]["relatives"]) == '[1]'))
    assert (str(sorted([x for x in tmp if x["citizen_id"] == 3][0]["relatives"]) == '[1]'))

    tmp, _ = print_request("GET", "/imports/%d/citizens/birthdays" % resp.json()["data"]["import_id"])

    assert (tmp.status_code == 200)

    tmp = tmp.json()["data"]

    for idx in range(1,13):
        if idx in [11,4]:
            assert (tmp[str(idx)][0]["presents"] == 1)
            assert (tmp[str(idx)][0]["citizen_id"] == 1)
        elif idx == 12:
            assert (len(tmp[str(idx)]) == 2)
        else:
            assert (len(tmp[str(idx)]) == 0)


    tmp, _ = print_request("PATCH", "/imports/%d/citizens/3" % resp.json()["data"]["import_id"], {
        "relatives" : []
    })

    assert (tmp.status_code == 200)

    tmp, _ = print_request("GET", "/imports/%d/citizens" % resp.json()["data"]["import_id"])
    assert (tmp.status_code == 200)
    tmp = tmp.json()["data"]

    assert (str(sorted([x for x in tmp if x["citizen_id"] == 1][0]["relatives"]) == '[2]'))
    assert (str(sorted([x for x in tmp if x["citizen_id"] == 2][0]["relatives"]) == '[1]'))
    assert (str(sorted([x for x in tmp if x["citizen_id"] == 3][0]["relatives"]) == '[]'))
