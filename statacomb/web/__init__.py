
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
STRPTIME_ISO = '%Y-%m-%d %H:%M'


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
        scale = 1
    scale = int(scale)

    start_time = request.query_data.get('start_time', [None])[0]
    if start_time:
        start_time = datetime.strptime(start_time, STRPTIME_ISO)

    end_time = request.query_data.get('end_time', [None])[0]
    if end_time:
        end_time = datetime.strptime(end_time, STRPTIME_ISO)

    if not end_time:
        if not start_time:
            end_time = datetime.now()
        else:
            end_time = start_time + (40 * timedelta(seconds=scale))

    if not start_time:
        start_time = end_time - (40 * timedelta(seconds=scale))

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
    try:

        query = '''
            WITH
                -- Flatten values->>* into a table
                flat_fields AS (
                    SELECT ts, CAST(EXTRACT(epoch FROM ts) AS INT) / %(scale)s AS tsa, %(fields)s
                    FROM records
                ),
                -- Generate a continuous time series
                filled_times AS (
                    SELECT EXTRACT(epoch FROM generate_series(%%s, %%s, '%(minutes)s minute')) AS tsa, 0 as blank_count
                ),
                -- Aggregate values from flat_fields
                sample_counts AS (
                    SELECT tsa * %(scale)s AS tsa, %(aggregate)s
                    FROM flat_fields
                    GROUP BY tsa
                )
            SELECT filled_times.tsa AS ts, %(coalesce)s
            FROM filled_times
            LEFT OUTER JOIN sample_counts USING (tsa)
            ORDER BY filled_times.tsa
        ''' % {
            'scale': scale,
            'minutes': scale // 60,
            'fields': ', '.join([
                'CAST(values->>%s AS INT) AS %s' % (QuotedString(field), field)
                for field in fields
            ]),
            'aggregate': ', '.join([
                '%s(%s) AS %s' % (mode.upper(), field, field)
                for field in fields
            ]),
            'coalesce': ', '.join([
                'COALESCE(sample_counts.%s, filled_times.blank_count) AS %s' % (field, field,)
                for field in fields
            ]),
        }

        cursor.execute(query, [
            start_time,
            end_time,
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
