// This file is entry point and bootstraps express application

const express = require('express');
const path = require('path');
const passport = require('passport');
const PythonShell = require('python-shell');

const configureServer = require('./server');
const configureRoutes = require('./routes');

const app = express();

const options = {
  scriptPath: path.resolve(__dirname, '../python'),
};
var pyshell = new PythonShell('prototype_v05.py', options);
configureServer(app, passport);
configureRoutes(app, passport, pyshell);

app.listen(5000);
// app.listen(8080, argv.fe_ip);
// console.log("App listening on port 8080");
