#!/bin/sh
echo "Waiting for Postgres..."
until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER"; do
  sleep 2
done

echo "Postgres ready. Running migrations and collectstatic..."
python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"
