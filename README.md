# Proto ruby python example

This is an squeletton for the proto types between ruby and python.

The app.py file creates a python flask app with the proto, loading a request and returning the results

## How to re-generate proto file

After changing something to the proto, it can be regenerated with this comand:

```bash
make proto-gen
```
Protifles are generated under the protopython folder and ruby folder

## How to run the flask api

Flask api can be built and run with the following commands:

To build the app:
```bash
make build
```

To run locally
```bash
make run
```

To deploy to Sagemaker:
```bash
make deploy
```
