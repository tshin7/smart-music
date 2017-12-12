// This file is entry point and bootstraps express application

const express = require('express');
const path = require('path');
const passport = require('passport');

const configureServer = require('./server');
const configureRoutes = require('./routes');

const app = express();

configureServer(app, passport);
configureRoutes(app, passport);

app.listen(5000);
// app.listen(8080, argv.fe_ip);
// console.log("App listening on port 8080");
