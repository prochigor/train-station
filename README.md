# train-station



## Description
In this api you can manage proces on the train station, users can read information about stations, routes,
trains with types and journey (Data type format: `YYYY-mm-dd hh:mm`) with general information, but only admins can 
create new elements, but everything can create new orders with tickets. To update or delete info, you can use 
admin panel, where you can use all CRUD possibilities, if you have a permission. Welcome to train station.

# You can see all endpoints to api here `http://127.0.0.1:8000/api/doc/swagger/`

## Guideline how to use

1) Open terminal and clone the repo (`git clone `)

2) Open cloned folder

3) Activate venv on the project
- Open terminal and write: 
  - On Windows: (`python -m venv venv`) and (`venv\Scripts\activate`)
  - On Mac: (`python3 -m venv venv`) and (`source venv/bin/activate`)

4) Create `.env` file in root directory with data to BD, example in `.env.sample`
   - POSTGRES_DB= `BD name`
   - POSTGRES_USER= `BD's user name`
   - POSTGRES_PASSWORD= `password to BD`
   - POSTGRES_HOST= `Host to BD`

# Run without docker:

1) Install needed requirements:
  Write in terminal (`pip install -r requirements.txt`)

2) Install PostgresSQL and create db

3) Migrate
  Write in terminal (`python manage.py migrate`)

4) Run server
  Write in terminal `python manage.py runserver`

5) Open page with link in terminal

6)  Create user on terminal: 
- Write on terminal `python manage.py createsuperuser`
`Examle data`
- `email: admin@user.com`
- `Password: 1qazcde3`

7) Add more data and use for free.

8) (Data type format: `YYYY-mm-dd hh:mm`)

# Run with docker

1) Install docker if don't have.

2) pull docker container
`docker pull prochihor/tarin_station-app`

3) run container
`docker-compose build`
`docker-compose up`

4) Open page with link in terminal or the page `http://127.0.0.1:8000/`
