#!/bin/bash

git config --global --add safe.directory /app

if [[ ! -f ".vscode/launch.json" ]]; then
    cp .vscode/launch.json.default .vscode/launch.json
fi
if [[ ! -f ".vscode/settings.json" ]]; then
    cp .vscode/settings.json.default .vscode/settings.json
fi


./manage.py migrate

./manage.py collectstatic

./manage.py runserver 0.0.0.0:8000
