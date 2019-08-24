import time
from flask import Flask, request, abort
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from dateutil import relativedelta # leap year!
import os
import json
import fcntl
import utils

app = Flask(__name__)

db = create_engine('postgresql://%(USER)s:%(PASS)s@%(HOST)s/%(DBNAME)s' % dict(
        DBNAME=os.environ.get("POSTGRESS_DBNAME", ""),
        USER=os.environ.get("POSTGRESS_USER", ""),
        HOST=os.environ.get("POSTGRESS_HOST", ""),
        PASS=os.environ.get("POSTGRESS_PASS", "")
))


@app.route('/imports', methods=['POST'])
def insert_import():
    if not request.json:
        abort(400, "NE JSON!")

    try:
        citizens, relatives = utils.validate_citizens_json(request.json)
    except Exception as e:
        abort(400, repr(e))

    db_conn = db.connect()

    new_id = pd.read_sql("INSERT INTO imports (timestamp) VALUES (%d) RETURNING id" % int(time.time()), db_conn)["id"].iloc[0]

    lock = open('/var/lock/%d' % new_id, 'a+')
    fcntl.flock(lock, fcntl.LOCK_EX)

    try:

        citizens["import_id"] = new_id
        relatives["import_id"] = new_id

        transaction = db_conn.begin()

        try:
            citizens.to_sql("citizens", db_conn, if_exists='append', index=False, chunksize=1000)
            relatives.to_sql("relatives", db_conn, if_exists='append', index=False)
        except Exception as e:
            transaction.rollback()
            db_conn.close()
            abort(500, repr(e))

        transaction.commit()

        db_conn.close()
        return {"data":{"import_id":new_id}}, 200

    finally:
        lock.close()


@app.route('/imports/<int:import_id>/citizens/<int:citizen_id>', methods=['PATCH'])
def update_citizen(import_id, citizen_id):

    if not request.json:
        abort(400, "NE JSON!")

    db_conn = db.connect()

    lock = open('/var/lock/%d' % import_id, 'a+')
    fcntl.flock(lock, fcntl.LOCK_EX)

    try:

        citizen_now = pd.read_sql("SELECT * FROM citizens WHERE import_id = %d AND citizen_id = %d" % (
            import_id,
            citizen_id
        ), db_conn)

        if citizen_now.shape[0] == 0:
            abort(400, "Citizen not found")

        if citizen_now.shape[0] > 1:
            abort(500, "DB fuckuped")

        citizen_now = citizen_now.iloc[0].to_dict()

        try:
            citizen_now, updates = utils.apply_citizen_patch(citizen_now, request.json)
        except Exception as e:
            abort(400, repr(e))

        transaction = db_conn.begin()

        if len(updates) > 0:
            req = "UPDATE citizens SET " + ", ".join([x[0] for x in updates]) + " WHERE id = %d" % citizen_now["id"]
            db_conn.execute(req, [x[1] for x in updates])

        if "relatives" in request.json:
            utils.set_relatives(db_conn, import_id, citizen_id, request.json["relatives"])
            citizen_now = utils.return_citizen(citizen_now)
        else:
            citizen_now = utils.return_citizen(citizen_now, db_conn)

        transaction.commit()
        db_conn.close()

        return json.dumps({"data":citizen_now}, encoding='utf-8', ensure_ascii=False, indent = 2), 200

    finally:
        lock.close()


@app.route('/dbcheck', methods = ['GET'])
def check_db_conn():
    try:
        db_conn = db.connect()
        db_conn.close()
        return {"success":True}, 200
    except Exception as e:
        return {"success":False, "error":repr(e)}, 500


@app.route('/imports/<int:import_id>/citizens', methods = ['GET'])
def get_import(import_id):

    db_conn = db.connect()

    lock = open('/var/lock/%d' % import_id, 'a+')
    fcntl.flock(lock, fcntl.LOCK_EX)

    try:

        citizens = pd.read_sql("SELECT * FROM citizens WHERE import_id = %d" % import_id, db_conn)

        if citizens.shape[0] > 0:

            relatives = pd.read_sql("SELECT * FROM relatives WHERE import_id = %d" % import_id, db_conn)

            rels = {}
            for c_from, c_to in zip(relatives.citizen_from, relatives.citizen_to):
                if c_from not in rels:
                    rels[c_from] = []
                rels[c_from].append(c_to)

            result = [utils.return_citizen(x[1].to_dict()) for x in citizens.iterrows()]
            for idx in range(len(result)):
                if result[idx]["citizen_id"] in rels:
                    result[idx]["relatives"] = rels[result[idx]["citizen_id"]]
                else:
                    result[idx]["relatives"] = []

            result = json.dumps({"data":result}, encoding='utf-8', ensure_ascii=False, indent = 2)

            db_conn.close()
            return result, 200
        else:
            abort(404, "Import not found")

    finally:
        lock.close()


@app.route('/imports/<int:import_id>/citizens/birthdays', methods = ['GET'])
def get_bithdays(import_id):

    db_conn = db.connect()

    lock = open('/var/lock/%d' % import_id, 'a+')
    fcntl.flock(lock, fcntl.LOCK_EX)

    try:


        birthdays = pd.read_sql("""
        SELECT month, citizen_id, COUNT(1) as "presents" FROM
            (SELECT
            relatives.citizen_from as "citizen_id",
            EXTRACT(MONTH FROM to_timestamp(citizens.birth_date)) as "month"
            FROM relatives JOIN citizens
            ON citizens.import_id = relatives.import_id
            AND citizens.citizen_id = relatives.citizen_to
            WHERE relatives.import_id = %d) as tmp
        GROUP BY month, citizen_id
        """ % import_id, db_conn)

        result = {"data":{str(x):[] for x in range(1,13)}}

        for idx in range(birthdays.shape[0]):
            result["data"][str(int(birthdays.month.iloc[idx]))].append({
                "citizen_id" : birthdays.citizen_id.iloc[idx],
                "presents" : birthdays.presents.iloc[idx]
            })

        db_conn.close()

        return json.dumps(result, indent = 2), 200

    finally:
        lock.close()


@app.route('/imports/<int:import_id>/towns/stat/percentile/age', methods = ['GET'])
def get_age_percentiles(import_id):

    db_conn = db.connect()

    lock = open('/var/lock/%d' % import_id, 'a+')
    fcntl.flock(lock, fcntl.LOCK_EX)

    try:

        birthdates = pd.read_sql("""
            SELECT town, birth_date
            FROM citizens
            WHERE import_id = %d
        """ % import_id, db_conn)

        # birthdates["age"] = birthdates.birth_date.apply(lambda x : np.floor((time.time() - x)/3600./24./365.))
        # leap year!
        birthdates["age"] = birthdates.birth_date.apply(lambda x : relativedelta.relativedelta(
            pd.Timestamp(int(time.time()), unit = 's'),
            pd.Timestamp(x, unit='s')).years
        )

        if birthdates.shape[0] == 0:
            abort(404, "Import not found")

        result = {"data":[]}

        for town in birthdates.town.drop_duplicates():
            percentiles = np.percentile(birthdates[birthdates.town == town].age, [50,75,99], interpolation='linear')
            result["data"].append({
                "town" : town,
                "p50" : percentiles[0],
                "p75" : percentiles[1],
                "p99" : percentiles[2],
            })

        db_conn.close()

        return json.dumps(result, encoding='utf-8', ensure_ascii=False, indent = 2), 200

    finally:
        lock.close()