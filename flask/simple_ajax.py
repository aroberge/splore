'''Simple ajax demo using flask'''

from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/')
def index():
    return html_content  # see below


@app.route('/_add_numbers')
def add_numbers():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a + b)


# For simplicity, we'll use jQuery
html_content = '''
<!DOCTYPE html>
<html lang="en">
  <head>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
    <script type=text/javascript>
      $(function() {
        $('#calculate').bind('click', function() {
          $.getJSON('/_add_numbers', {
            a: $('input[name="a"]').val(),
            b: $('input[name="b"]').val()
          }, function(data) {
            $("#result").text(data.result);
          });
          return false;
        });
      });
    </script>
  </head>
  <body>
    <h1>Adding two number using ajax</h1>

    <form>
      <input type="text" size="5" name="a"> +
      <input type="text" size="5" name="b"> =
      <span id="result">?</span>
    </form>
    <p><button id="calculate">Calculate</button></p>

  </body>
</html>
'''

if __name__ == '__main__':
    app.run()
