cd ./venv/Scripts
sphinx-build.exe -b html -D language=['en','ja'] -j auto -a -n -T -W --keep-going ./../../docs _build/html
pause