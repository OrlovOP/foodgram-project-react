#!/bin/bash
set -e
exec bash -c "gunicorn --bind 0.0.0.0:8000 foodgram.wsgi"