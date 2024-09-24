# tests for the code in /src/

- to avoid import errors, the tests are run from the ./src directorty
```bash
cd src
python -m unittest discover -s tests -p 'test_*.py'
# or
python -m unittest  
```
