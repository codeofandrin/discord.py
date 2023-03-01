cd ./venv/Scripts
black --check --diff ./../../discord ./../../examples
cd ./../..

:: reformat file: black ./../../discord ./../../examples