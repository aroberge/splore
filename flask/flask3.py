from flask import Flask

app = Flask(__name__)

@app.route("/integer_test/<int:value>")
def int_test(value):
    print(value)
    return "Integer ok"

@app.route("/float_test/<float:value>")
def float_test(value):
    print(value)
    return "Float ok"

@app.route("/path_test/<path:value>")
def path_test(value):
    print(value)
    return "Path ok"


@app.route("/user/<name>")
def greet_user(name):
    return "<h2>Hello {}</h2>".format(name)

@app.route("/")
def hello_world():
    return "Hello, World! "

if __name__ == "__main__":
    app.run(debug=True)
