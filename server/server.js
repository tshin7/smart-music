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
const CircularJSON = require('circular-json');
const cycle = require('cycle');
var stringify = require('json-stringify-safe');

const configureServer = (app, passport) => {
  const options = {
    scriptPath: path.resolve(__dirname, '../python'),
  };
  var pyshell = new PythonShell('prototype_v05.py', options);


  // configuration
  // mongoose.connect('mongodb://' + argv.be_ip + ':80/my_database');

  // express session middleware
  app.set('trust proxy', 1) // trust first proxy
  app.use(session({
    secret: 'keyboard cat',
    resave: false,
    saveUninitialized: true,
  }));

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
    res.render('home.ejs', {
      user: req.user // get the user out of session and pass to template
    });
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

  app.get('/start', function(req, res) {
    pyshell.send('add_instrument');
    res.send('Start');
  });

  app.get('/play', function(req, res) {
    pyshell.send('play');
    res.send('Play');
  });

  app.get('/stop', function(req, res) {
    pyshell.send('stop');
    res.send('Stop');
  });

  app.get('/add-instrument', function(req, res) {
    pyshell.send('add_instrument');
    res.send('Added instrument');
  });

  app.get('/api/python', function(req, res) {

    const options = {
      scriptPath: path.resolve(__dirname, '../python'),
    };
    var pyshell = new PythonShell('prototype_v05.py', options);
    pyshell.send('play')
    pyshell.on('message', function (message) {
      // received a message sent from the Python script (a simple "print" statement)
      console.log(message);
      res.send(message);
    });

    if (req.session.num) {
      req.session.num++;
    } else {
      req.session.num = 1;
    }
    console.log('###');
    console.log(req.session);

    // end the input stream and allow the process to exit
    // pyshell.end(function (err) {
    //   if (err) throw err;
    //   console.log('finished');
    // });

  });

};

module.exports = configureServer;
