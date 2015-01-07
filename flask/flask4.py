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


# explicitly specify error code
@app.route("/user/<name>")
def greet_user(name):
    if name.lower() == name:    # not a real person then, is it? ;-)
        return "Not found", 404
    return "<h2>Hello {}</h2>".format(name), 200

@app.route("/")
def hello_world():
    return "Hello, World! "

if __name__ == "__main__":
    app.run(debug=True)
