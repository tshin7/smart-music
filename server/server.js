const express = require('express');
const path = require('path');
const helmet = require('helmet'); // sets some http header for security
const flash = require('connect-flash');
const mongoose = require('mongoose'); // mongoose for mongodb
const morgan = require('morgan'); // log requests to the console
const bodyParser = require('body-parser'); // pull information from HTML POST
const cookieParser = require('cookie-parser');
const session = require('express-session');
const PythonShell = require('python-shell')
const methodOverride = require('method-override'); // simulate DELETE and PUT
const argv = require('optimist').argv;

const configureServer = (app, passport) => {
  // configuration
  // mongoose.connect('mongodb://' + argv.be_ip + ':80/my_database');

  app.use(morgan('dev')); // log every request to the console
  app.use(helmet());
  app.use(cookieParser()); // read cookies (needed for auth)
  app.use(bodyParser.urlencoded({ extended: true })); // parse application/x-www-form-urlencoded
  app.use(bodyParser.json());
  app.use(methodOverride());

  app.set('view engine', 'ejs'); // set up ejs for templating
  app.set('views', path.resolve(__dirname, '../client/views/pages')); // change default view directory

  // Serve static files with express static middleware function
  app.use('/controllers', express.static(path.resolve(__dirname, '../client/controllers')));

  app.get('/', function(req, res) {
    res.send('hello world');
  });

  app.get('/home', function(req, res) {
    // console.log(req.user);
    res.render('home.ejs', {
      user: req.user // get the user out of session and pass to template
    });
  });

  // Answer API requests.
  app.get('/api', function(req, res) {
    res.set('Content-Type', 'application/json');
    res.send('{"message":"Hello from the custom server!"}');
  });

  app.get('/python', function(req, res) {

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

};

module.exports = configureServer;
