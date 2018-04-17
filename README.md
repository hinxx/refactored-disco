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


Requests:

POST http://hinkocmbp.esss.lu.se:5000
Accept: application/json
Content-Type: application/json

{ "PVs": ["MEBT-010:PBI-BPM-001:Xpos" ]}

Equivalent curl command (Replace <password> with real password):
curl -i -H Accept:application/json -H Content-Type:application/json -X POST http://hinkocmbp.esss.lu.se:5000 -H Content-Type: application/json -d '{ "PVs": ["MEBT-010:PBI-BPM-001:Xpos" ]}'

Responses:

[
 {
 "PVData": [
 -1.8052325248718262,
 1.009652018547058,
 -1.3055641651153564,
 ...
 ],
 "PVName": "MEBT-010:PBI-BPM-001:Xpos",
 "Rowid": 683821,
 "TimeStamp": "2018-03-07 13:28:46.614998"
 },
 {
 "PVData": [
 0.596241295337677,
 -0.7258983850479126,
 ...
 ],
 "PVName": "MEBT-010:PBI-BPM-001:Xpos",
 "Rowid": 683830,
 "TimeStamp": "2018-03-07 13:28:49.636052"
 },
...
]

