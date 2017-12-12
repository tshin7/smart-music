// Routes index

const start = require('./start');
const home = require('./home');
const sonicPiApi = require9('./sonicPiApi');

// route middleware to make sure a user is logged in
const isLoggedIn = (req, res, next) => {
  // if user is authenticated in the session, carry on
  if (req.isAuthenticated()) {
    return next();
  }
  // if they aren't redirect them to start page
  res.redirect('/');
}

const configureRoutes = (app, passport) => {
  start(app);
  home(app, isLoggedIn);
  sonicPiApi(app, isLoggedIn);

};

module.exports = configureRoutes;
