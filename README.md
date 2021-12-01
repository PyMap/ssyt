# Systema sociedad y territorio

* Root

```
virtualenv venv --python=python3.8
source venv/bin/activate
pip install -r requirements.txt

streamlit run st.main.py
```
* Develop mode

```
virtualenv venv --python=python3.8
source venv/bin/activate
python setup.py develop
pip install -r requirements-dev.txt

streamlit run st.main.py

```
