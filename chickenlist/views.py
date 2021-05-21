from django.shortcuts import render

import datetime as datetime

import os
import psycopg2
import hashlib


def show_date_status(request, hashcode='', rand_string=''):

    hashcode = request.GET.get('hc')
    random_string = request.GET.get('rs')

    if hashcode and random_string:

        # Replace for Production!

        username = os.environ['DBUSER']
        hostname = os.environ['DBHOST']
        password = os.environ['DBPASSWD']
        name = os.environ['DBNAME']

        connection = psycopg2.connect(f"user={username} host={hostname} password={password} dbname={name}")

        # Replace ende

        cur = connection.cursor()
        cur.execute("""SET SCHEMA 'chickenlist';""")

        connection.commit()

        cur.execute("""SELECT nachname FROM besitzer;""")
        connection.commit()
        owners = cur.fetchall()

        last_name = ""
        termin_id = -1

        found = False

        for owner in owners:
            cur.execute("""SELECT IID FROM impftermin;""")
            connection.commit()
            iids = cur.fetchall()

            for iid in iids:
                test_string = hashlib.md5(str(owner[0].lower() + str(iid[0]) + random_string).encode()).hexdigest()

                if test_string == hashcode:
                    last_name = owner[0]
                    termin_id = iid[0]

                    found = True
                    break

                if found:
                    break

        if found:
            cur.execute("""SELECT datum FROM impftermin WHERE IID = %s;""", [termin_id])
            connection.commit()
            date = cur.fetchone()

            date = date[0]


            today = datetime.datetime.now().date()

            days_since_last = (today - date)
            days_since_last = days_since_last.days

            state = ""
            color = ""

            if days_since_last <= 92:
                state = "Sie haben noch Zeit bis zu Ihrem nächsten Impftermin."
                color = "Green"
            elif days_since_last <= 123:
                state = "Sie sollten sich im laufe der nächsten 4 Wochen einen Termin besorgen."
                color = "Orange"
            else:
                state = "Sie sollten sich umgehend einen neuen Impftermin besorgen!"
                color = "FireBrick"

            quarter_year = datetime.timedelta(days=92)
            next_date = date + quarter_year

            response = render(request, "chickenlist/found.html",
                              {"title": f"Impftermin {last_name}",
                               "state": state, "color": color,
                               "last_date": datetime.datetime.strftime(date, "%d.%m.%Y"),
                               "next_date": datetime.datetime.strftime(next_date, "%d.%m.%Y"),
                               "days_gone": days_since_last})
        else:
            response = render(request, "chickenlist/not_found.html", {"title": f"Impftermin Fehler"})
    else:
        response = render(request, "chickenlist/404.html", {"title": f"404 Impftermin"})

    connection.close()
    return response


def show_page_not_found(request, url=''):
    return render(request, "chickenlist/404.html", {"title": f"404 Impftermin"})

