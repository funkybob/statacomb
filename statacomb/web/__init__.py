
from datetime import datetime, timedelta
from decimal import Decimal
import json
import os
import re

import antfarm
from antfarm.views.static import ServeStatic
from antfarm.views.urls import url_dispatcher

from psycopg2.extensions import QuotedString
from psycopg2.extras import DictCursor

from statacomb import utils

BASE_DIR = os.path.dirname(__file__)
rel = lambda x: os.path.join(BASE_DIR, x)

FIELD_RE = re.compile(r'^\w+$')

urls = url_dispatcher(
    (r'^/static/(?P<path>.*)', ServeStatic(rel('static/'))),
)


class JsonEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(JsonEncoder, self).default(o)

encoder = JsonEncoder()

def as_json(data, **kwargs):
    return antfarm.Response(
        encoder.encode(data),
        content_type='application/json',
        **kwargs
    )


@urls.register(r'^/$')
def index(request):
    return antfarm.Response(open(rel('templates/index.html')))


@urls.register(r'^/info/values/$')
def info_values(request):
    '''
    Return info about the stats
    '''
    cursor = request.conn.cursor()
    try:
        cursor.execute('''
            SELECT DISTINCT json_object_keys(values) FROM records;
        ''')
        return as_json([row[0] for row in cursor])
    finally:
        cursor.close()


@urls.register(r'^/info/sources/$')
def into_sources(request):
    '''
    Return the list of available sources.
    '''
    cursor = request.conn.cursor()
    try:
        cursor.execute('''SELECT DISTINCT source FROM records;''')
        return as_json([row[0] for row in cursor])
    finally:
        cursor.close()


@urls.register(r'^/data/$')
def data(request):
    '''
    '''

    scale = request.query_data.get('scale', [None])[0]
    if scale is None:
        scale = 300
    else:
        scale = int(scale)

    duration = request.query_data.get('duration', [None])[0]
    if duration is None:
        duration = 30
    duration = timedelta(minutes=int(duration))

    start_time = request.query_data.get('start_time', [None])[0]
    if start_time is None:
        start_time = datetime.now() - duration
    else:
        start_time = datetime.fromtimestamp(int(start_time))

    # Safety first
    fields = [
        field
        for field in request.query_data.get('field', ['total'])
        if FIELD_RE.match(field)
    ]

    mode = request.query_data.get('mode', ['sum'])[0]
    if mode not in ['sum', 'avg']:
        mode = 'sum'

    cursor = request.conn.cursor()
    safe_fields = [QuotedString(field) for field in fields]
    try:

        query = '''
            SELECT i.tsa * %%s AS ts, %s
            FROM (
                SELECT CAST(EXTRACT(EPOCH FROM ts) AS INT) / %%s AS tsa, %s
                FROM records
                -- WHERE ts > %%s
                -- AND ts < %%s
            ) AS i
            GROUP BY i.tsa
            ORDER BY i.tsa ASC
        ''' % (
            ','.join([
                '%s(%s) AS %s' % (mode.upper(), field, field)
                for field in fields
            ]),
            ','.join([
                'CAST(values->>%%s AS INT) as %s' % (field,)
                for field in fields
            ]),
        )

        cursor.execute(query, [
            scale,
            scale,
        ] + safe_fields + [
            start_time,
            start_time + duration
        ])

        return as_json([dict(row) for row in cursor])
    finally:
        cursor.close()


def connect(request):
    '''
    Connect to the DB
    '''
    request.conn = utils.get_db_connection(
        request.app.config,
        cursor_factory=DictCursor
    )

    try:
        return urls(request)
    finally:
        request.conn.close()
