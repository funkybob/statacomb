
import egress


def get_db_connection(opts, **kwargs):

    return egress.connect(
        dsn=opts.dsn,
        database=opts.dbname,
        user=opts.dbuser,
        password=opts.dbpassword,
        host=opts.dbhost,
        port=opts.dbport,
        **kwargs
    )
