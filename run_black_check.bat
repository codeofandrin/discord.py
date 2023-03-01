cd ./venv/Scripts
black --check --diff ./../../discord ./../../examples
cd ./../..
pause

:: reformat file: black ./../../discord ./../../examples