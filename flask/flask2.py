from flask import Flask

app = Flask(__name__)

@app.route("/user/<name>")
def greet_user(name):
    return "<h2>Hello {}</h2>".format(name)

@app.route("/")
def hello_world():
    return "Hello, World! "

if __name__ == "__main__":
    app.run(debug=True)
