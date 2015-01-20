<!doctype html>
<html>
<head></head>
<body>


% name = "Bob"  # a line of python code
<p>Some plain text in between</p>
%
  name = name.title().strip()
%
<p>More plain text</p>

<p>Edit the task with ID = {{no}}</p>
<form action="/edit/{{no}}" method="get">
<input type="text" name="task" value="{{old[0]}}" size="100" maxlength="100">
<select name="status">
<option>open</option>
<option>closed</option>
</select>
<br/>
<input type="submit" name="save" value="save">
</form>

</body>
</html>
