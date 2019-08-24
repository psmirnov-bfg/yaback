# coding=utf-8

import random
import string
import time
import requests

from test import URL

TOWNS = ["Москва", "Uagadugu", "'дефолт city'"]


def random_string(length):
    chars = string.letters + string.digits + "'" + '"' + "-(){}[] " + u"абвгдейкаэюяьъ"
    return ''.join([random.choice(string.letters)] + [random.choice(chars) for x in range(length)])

def generate_random_citizen(citizen_id):
    return {
        "citizen_id": citizen_id,
        "town": random.choice(TOWNS),
        "street": random_string(10),
        "building": random_string(5),
        "apartment": random.choice(range(1,1001)),
        "name": random_string(30),
        "birth_date": "%d.%d.%d" % (
            random.choice(range(1,29)),
            random.choice(range(1,13)),
            random.choice(range(1900, 2019))),
        "gender": random.choice(["male", "female"]),
        "relatives" : []
    }

def generate_random_dataset(n_citizens, n_relatives):

    citizens = [generate_random_citizen(x) for x in range(n_citizens)]

    relatives = {(-1,-1)}

    citizen_1 = -1
    citizen_2 = -1

    for i in range(n_relatives):

        while (citizen_1, citizen_2)  in relatives:

            cit_1 = random.choice(range(n_citizens))
            cit_2 = random.choice(range(n_citizens))

            citizen_1 = min(cit_1, cit_2)
            citizen_2 = max(cit_1, cit_2)

        relatives.add((citizen_1, citizen_2))

        citizens[citizen_1]["relatives"].append(citizen_2)

        if citizen_1 != citizen_2:

            citizens[citizen_2]["relatives"].append(citizen_1)

    print "REALTIVES:", relatives

    return citizens


def test_big(n_citizens = 10000, n_relatives = 1000, n_updates = 1000):

    citizens = generate_random_dataset(10000, 1000)

    start = time.time()
    resp = requests.post(URL + '/imports', json={"citizens":citizens})

    print "INSERT:"
    print resp.text
    print time.time() - start

    assert time.time() - start < 10
    assert resp.status_code == 200

    impor_id = resp.json()["data"]["import_id"]

    start = time.time()
    resp = requests.get(URL + '/imports/%d/towns/stat/percentile/age' % impor_id)

    print "AGE PERCENTILE:"
    if resp.status_code != 200:
        print resp.text
    print time.time() - start

    assert time.time() - start < 10
    assert resp.status_code == 200

    start = time.time()
    resp = requests.get(URL + "/imports/%d/citizens/birthdays" % impor_id)

    print "BIRTHDAYS:"
    if resp.status_code != 200:
        print resp.text
    print time.time() - start

    assert time.time() - start < 10
    assert resp.status_code == 200

    updrels = {}
    new_rels_set = 0

    allcitizens = set(range(n_citizens))

    for idx in range(n_updates):

        if len(allcitizens) == 0:
            print "Citizens empty, enough updates"
            break

        citizen = random.choice(list(allcitizens))

        rel_count = random.choice([0, 1, 2, 5, 10])
        old_count = len(citizens[citizen]["relatives"])

        if rel_count - old_count + new_rels_set > n_relatives:
            continue

        listcitizens = list(allcitizens)
        random.shuffle(listcitizens)

        new_name = random_string(30)
        new_relaitves = listcitizens[:rel_count]

        for x in new_relaitves:
            allcitizens.remove(x)
        if citizen in allcitizens:
            allcitizens.remove(citizen)

        start = time.time()
        resp = requests.patch(URL + '/imports/%d/citizens/%d' % (impor_id, citizen), json = {
            "name" : new_name,
            "relatives" : new_relaitves
        })

        updrels[citizen] = (new_relaitves, new_name)

        print "UPDATE %d/%d:" % (idx + 1, n_updates)
        if resp.status_code != 200:
            print resp.text
        print time.time() - start

        assert time.time() - start < 10
        assert resp.status_code == 200

    resp = requests.get(URL + "/imports/%d/citizens" % impor_id)

    print "GET CITIZENS:"
    if resp.status_code != 200:
        print resp.text
    print time.time() - start

    assert time.time() - start < 10
    assert resp.status_code == 200

    for citizen in resp.json()["data"]:
        if citizen["citizen_id"] in updrels:
            assert citizen["name"] == updrels[citizen["citizen_id"]][1]
            assert str(sorted(citizen["relatives"])) == str(sorted(updrels[citizen["citizen_id"]][0]))

    print "AGE PERCENTILE:"
    if resp.status_code != 200:
        print resp.text
    print time.time() - start

    assert time.time() - start < 10
    assert resp.status_code == 200

    start = time.time()
    resp = requests.get(URL + "/imports/%d/citizens/birthdays" % impor_id)

    print "BIRTHDAYS:"
    if resp.status_code != 200:
        print resp.text
    print time.time() - start

    assert time.time() - start < 10
    assert resp.status_code == 200