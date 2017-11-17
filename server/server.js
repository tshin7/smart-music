const express = require('express');
const app = express();
const path = require('path');
const PythonShell = require('python-shell');
const mongoose = require('mongoose'); // mongoose for mongodb
const morgan = require('morgan'); // log requests to the console
const bodyParser = require('body-parser'); // pull information from HTML POST
const methodOverride = require('method-override'); // simulate DELETE and PUT
const argv = require('optimist').argv;

const PORT = process.env.PORT || 5000;

// configuration
// mongoose.connect('mongodb://' + argv.be_ip + ':80/my_database');

app.use(morgan('dev')); // log every request to the console
app.use(bodyParser.urlencoded({'extended':'true'})); // parse application/x-www-form-urlencoded
app.use(bodyParser.json()); // parse application/json
app.use(methodOverride());

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

app.listen(PORT, argv.fe_ip, function () {
  console.log(`Listening on port ${PORT}`);
});
