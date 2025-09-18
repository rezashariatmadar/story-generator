web: gunicorn story_generator.wsgi:application --bind 0.0.0.0:$PORT
release: python verify_build.py && python manage.py migrate 