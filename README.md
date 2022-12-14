# Livecode - CI/CD with twitter REST API with AWS & Postgres

## Let's inspect quickly the code base

This app is a basic REST API that we will plug to a postgres database.
This API manipulates `tweets resources` which allows to :

- Create tweets
- Update them
- Delete them
- List them

Let's understand the basic interaction between modules and components.

- `app` folder contains the twitter REST logic
- `tests` contains some unit & integration test that we will run to test our code
- `Procfile` contains some instructions we want our Beanstalk to launch to start our applications
- `config.py` & `.env` are some configurations files used to connect our flask application to our postgres database


## 1 - Set up the databases with postgres


###  Alembic setup

We need a local database for our application, one for production, one to run the test.

```bash
winpty psql -U postgres -c "CREATE DATABASE twitter_api"

# MAC OS
# createdb twitter_api
```

Here is how we are going to achieve this goal. First we need to create a new database locally:

```bash
winpty psql -U postgres -c "CREATE DATABASE twitter_api_test"

# MAC OS
# createdb twitter_api_test
```

Now we can use Alembic (run `pipenv graph` to see where it stands)!

```bash
pipenv run flask db init

```

This command has created a `migrations` folder, with an empty `versions` in it. Time to run the first migration with the creation of the `tweets` table from the `app/models.py`'s `Tweet` class.

```bash
pipenv run flask db migrate -m "Create tweets table"
```

Open the `migrations/versions` folder: can you see a first migration file? Go ahead, open it and read it! That's a file you **can** modify if you are not happy with what has been automatically generated. Actually that's something the tool tells you:

```bash
# ### commands auto generated by Alembic - please adjust! ###
```

When you are happy with the migration, time to run it against the local database:

```bash
pipenv run flask db upgrade
```

And that's it! There is now a `tweets` table in the `twitter_api` local database. It's empty for now, but it does exist!

### Adding a first tweet from a shell

We want to go the "manual testing route" to update the API controller code by adding manually a first Tweet in the database. It will validate that all our efforts to add SQLAlchemy are starting to pay off:

```bash
pipenv run flask shell
>>> from app import db
>>> from app.models import Tweet
>>> tweet = Tweet(text="Our first tweet!")
>>> db.session.add(tweet)
>>> db.session.commit()
# Did it work?
>>> db.session.query(Tweet).count()
>>> db.session.query(Tweet).all()
# Hooray!
```

## Check that the app works fine.


```
pipenv run flask run
```

#### Swagger documentation

The Flask-RESTx package comes with [swagger doc](https://flask-restx.readthedocs.io/en/stable/swagger.html) embeded. Run your server and access the root URL:

:point_right: [http://localhost:5000](http://localhost:5000)

Can you see the documentation? You can try your endpoints right within it!

---

## Setting up Github Actions for CI

Setting up GitHub Actions for a project where you have a real PostgreSQL database is not as trivial as for a project without a database. Let's see how we can take the **configuration of GitHub Actions** already mentioned:

```bash
mkdir -p .github/workflows
touch .github/workflows/first-workflow.yml
```

```yml
# .github/workflows/first-workflow.yml
name: Build and Tests

on: push

jobs:
  build:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:latest
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: twitter_api_test
        ports:
          - 5432:5432
        # needed because the postgres container does not provide a healthcheck
        options: --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5

    steps:
    - uses: actions/checkout@v2
    - name: Set up Python 3.9
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    - name: psycopg2 prerequisites
      run: sudo apt-get install libpq-dev
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pipenv
        pipenv install --dev
    - name: Test with nose
      run: |
        pipenv run nosetests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost/twitter_api_test
```

Version & push this change. Then go to your Github repository and check out the `Actions` tab. You should see a new "workflow run" there with the name of your commit. You can click on it and then on "Build" to see the build in real time.


### Deploy on Elastic Beanstalk


You know the drill!

1. Create app

```
eb init
```

```
eb create
```

```
eb open
```

### Set up Postgres


To set up **Postgres** for production in AWS Beanstalk, let's go over the AWS console:

```
eb console
```

- Select "Configuration" on the left side bar, scroll down to "Database", and then select on "Edit".

- Instanciate a database with the following criterias and click on "Apply":

```
Engine: postgres
Engine version: 12.9 (mandatory sinc since db.t2.micro is not available with 13.1+)
Instance class: db.t2.micro
Storage: 5 GB
Username: pick any username
Password: pick any strong password
```

**In order to keep using the AWS Free Tier we need to pick `db.t2.micro instance`. RDS prices increase exponentially based on the instance chosen.**

After the environment update is done (it could takes several minutes), EB will automatically pass the following DB credentials to our twitter app:

```
RDS_DB_NAME
RDS_USERNAME
RDS_PASSWORD
RDS_HOSTNAME
RDS_PORT
```

Let's wait for the deployment to end. Tada! Here we go ????

### CD with CodePipeline

Let's go over the console and implement continuous deployment ????
