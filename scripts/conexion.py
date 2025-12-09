import os
from pathlib import Path
import sys

# Ensure project directory on path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Use environ to read the .env file
try:
    import environ
except Exception as e:
    print('ERROR: failed to import environ:', e)
    raise SystemExit(1)

env = environ.Env()
environ_path = BASE_DIR / 'misite' / 'environ.env'
if not environ_path.exists():
    print('ERROR: .env file not found at', environ_path)
    raise SystemExit(1)

environ.Env.read_env(env_file=environ_path)

# Read Postgres settings
PG = {
    'host': env('POSTGRESQL_HOST', default='localhost'),
    'port': env('POSTGRESQL_PORT', default='5432'),
    'dbname': env('POSTGRESQL_NAME', default='postgres'),
    'user': env('POSTGRESQL_USER', default='postgres'),
    'password': env('POSTGRESQL_PASS', default=''),
}

print('Attempting to connect to Postgres with:')
print(' host=', PG['host'], ' port=', PG['port'], ' dbname=', PG['dbname'], ' user=', PG['user'])

try:
    import psycopg2
except Exception as e:
    print('ERROR: failed to import psycopg2:', e)
    raise SystemExit(1)

try:
    conn = psycopg2.connect(host=PG['host'], port=PG['port'], dbname=PG['dbname'], user=PG['user'], password=PG['password'])
    cur = conn.cursor()
    cur.execute('SELECT version();')
    ver = cur.fetchone()
    print('Conecion exitosa')
    cur.close()
    conn.close()
except Exception as e:
    print('ERROR: connection failed:', repr(e))
    raise SystemExit(1)
