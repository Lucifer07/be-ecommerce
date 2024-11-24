python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mkdir static
python3 manage.py collectstatic --noinput