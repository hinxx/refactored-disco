                         / WebPV /

                 a minimal EPICS web client application


    ~ What is WebPV?

      A sqlite powered EPICS PV client application

    ~ How do I use it?

      1. edit the configuration in the factory.py file or
         export a WEBPV_SETTINGS environment variable
         pointing to a configuration file or pass in a
         dictionary with config values using the create_app
         function.

      2. install the app from the root of the project directory

         pip install --editable .

      3. instruct flask to use the right application

         export FLASK_APP="webpv.factory:create_app()"

      4. initialize the database with this command:

         flask initdb

      5. now you can run webpv:

         flask run

         the application will greet you on
         http://localhost:5000/

    ~ Is it tested?

      You betcha.  Run `python setup.py test` to see
      the tests pass.

In flask master checkout:

pip install --editable .

In flask-cors master checkout:

pip install --editable .

In this module checkout:

pip install --editable .
export FLASK_APP="webpv.factory:create_app()"
export FLASK_DEBUG=1

flask initdb
flask run --host=0.0.0.0

