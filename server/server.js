const express = require('express');
const path = require('path');
const PythonShell = require('python-shell');

const app = express();
const PORT = process.env.PORT || 5000;

// Priority serve any static files.
app.use(express.static(path.resolve(__dirname, '../react-ui/build')));

// Answer API requests.
app.get('/api', function (req, res) {
  res.set('Content-Type', 'application/json');
  res.send('{"message":"Hello from the custom server!"}');
});

app.get('/python', function (req, res) {

  const options = {
    scriptPath: path.resolve(__dirname, '../python'),
  };
  var pyshell = new PythonShell('assignment.py', options);
  pyshell.on('message', function (message) {
    // received a message sent from the Python script (a simple "print" statement)
    console.log(message);
    res.send(message);
  });

  // end the input stream and allow the process to exit
  pyshell.end(function (err) {
    if (err) throw err;
    console.log('finished');
  });
  res.send('');
});

// All remaining requests return the React app, so it can handle routing.
app.get('*', function(request, response) {
  response.sendFile(path.resolve(__dirname, '../react-ui/build', 'index.html'));
});

app.listen(PORT, function () {
  console.log(`Listening on port ${PORT}`);
});
