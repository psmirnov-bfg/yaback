import pandas as pd

FROM_GENDER = {"male":False,"female":True}
TO_GENDER = {True:"female",False:"male"}


def validate_int(x):
    if not isinstance(x, int):
        raise Exception("Not Int")
    return x


def validate_string_letter_or_digit(x):
    if not isinstance(x, unicode) and not isinstance(x, str):
        raise Exception("Not string", x)
    for char in x:
        if char.isalnum():
            return x
    raise Exception("No digit or letter")


def validate_not_empty_string(x):
    if not isinstance(x, unicode) and not isinstance(x, str):
        raise Exception("Not string", x)
    if len(x) > 0:
        return x
    raise Exception("Empty string")


def validate_date(x):
    return pd.to_datetime(x, format = "%d.%m.%Y").value / 10**9


def validate_gender(x):
    return FROM_GENDER[x]


CITIZEN_FIELDS = {
    "citizen_id" : validate_int,
    "town" : validate_string_letter_or_digit,
    "street" : validate_string_letter_or_digit,
    "building" : validate_string_letter_or_digit,
    "apartment" : validate_int,
    "name" : validate_not_empty_string,
    "birth_date" : validate_date,
    "gender" : validate_gender
}


def validate_citizens_json(data):

    if "citizens" not in data:
        raise Exception("No citizens")

    relatives = []
    citizens = {}

    for citizen in data["citizens"]:

        new_citizen = {}

        for field in CITIZEN_FIELDS:
            new_citizen[field] = CITIZEN_FIELDS[field](citizen[field])

        if new_citizen["citizen_id"] in citizens:
            raise Exception("Duplicated citizens")

        citizens[new_citizen["citizen_id"]] = new_citizen

        if len(citizen["relatives"]) != len(list(set(citizen["relatives"]))):
            raise Exception("Duplicated relatives")

        for relative in citizen["relatives"]:
            relatives.append((new_citizen["citizen_id"], relative))

    if len(relatives) > 2000:
        raise Exception("Too many relatives")

    relatives = pd.DataFrame(relatives, columns=['citizen_from', 'citizen_to'])

    merged = pd.merge(relatives, relatives,
                      left_on=['citizen_from', 'citizen_to'],
                      right_on=['citizen_to', 'citizen_from'])

    if merged.shape[0] != relatives.shape[0]:
        raise Exception("Invalid relative connections")

    return pd.DataFrame(citizens.values()), relatives


def return_citizen(citizen, db = None):
    citizen.pop("id")
    import_id = citizen.pop("import_id")
    citizen["gender"] = TO_GENDER[citizen["gender"]]
    citizen["birth_date"] = pd.to_datetime(citizen["birth_date"], unit='s').strftime("%d.%m.%Y")

    if db is not None:
        relatives = pd.read_sql("SELECT * FROM relatives WHERE import_id = %d AND citizen_from = %d" % (
            import_id,
            citizen["citizen_id"]
        ), db)
        citizen["relatives"] = list(relatives.citizen_to)

    return citizen


def apply_citizen_patch(old_citizen, patch):

    if "citizen_id" in patch:
        raise Exception("Cant patch citizen_id")

    updates = []

    for field in patch:
        if field in CITIZEN_FIELDS:
            old_citizen[field] = CITIZEN_FIELDS[field](patch[field])
            updates.append(("%s = %%s" % field, old_citizen[field]))
        else:
            if field != 'relatives':
                raise Exception("Unknown field", field)
            else:
                old_citizen[field] = patch[field]

    return old_citizen, updates


def set_relatives(db, import_id, citizen_id, relatives):

    db.execute("DELETE FROM relatives WHERE import_id = %d AND citizen_from = %d" % (
        import_id,
        citizen_id
    ))

    db.execute("DELETE FROM relatives WHERE import_id = %d AND citizen_to = %d" % (
        import_id,
        citizen_id
    ))

    pd.concat([pd.DataFrame({
        "import_id" : import_id,
        "citizen_from" : citizen_id,
        "citizen_to" : relatives
    }), pd.DataFrame({
        "import_id" : import_id,
        "citizen_from" : relatives,
        "citizen_to" : citizen_id
    })]).to_sql("relatives", db, if_exists='append', index=False)