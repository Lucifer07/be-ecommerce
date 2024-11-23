# Backend Ecommerce

## Installation

How to run :

note: min python 3.12.4

```bash
git clone git@github.com:Lucifer07/be-ecommerce.git
cd be-ecommerce
# create youre env
nano .env
#linux/mac
python3 -m venv venv
source venv/bin/activate
#windows
python -m venv venv
.\venv\Scripts\activate
# install
pip install -r requirements.txt
# migrate data
python manage.py migrate
# run
python manage.py runserver

# add product
#login as admin, access this endpoint
POST {host}/api/products/
```
## ENV FORMAT
```bash
ALLOWED_HOSTS=
DEBUG = 
SECRET_KEY = 
MONDAY_BOARD_ID=
MONDAY_API_KEY=
DB_NAME=
DB_USERNAME=
DB_PASSWORD=
DB_HOST=
DB_PORT=
AIRTABLE_API_KEY=
AIRTABLE_BASE_ID=
AIRTABLE_TABLE_NAME=
```
## License

[MIT](https://choosealicense.com/licenses/mit/)