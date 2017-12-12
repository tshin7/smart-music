'use strict';

(function () {


})();

function handleStartClick() {
  $.get('/start', function(data) {
    console.log(data);
    $('#start-button').hide();
    $('#stop-button').show();
  });
};

function handlePlayClick() {
  $.get('/play', function(data) {
    console.log(data);
    $('#play-button').hide();
    $('#add-instrument-button').hide();
    $('#stop-button').show();
  });
};

function handleStopClick() {
  $.get('/stop', function(data) {
    console.log(data);
    $('#stop-button').hide();
    $('#play-button').show();
    $('#add-instrument-button').show();
  });
};

function handleAddInstrumentClick() {
  $.get('/add-instrument', function(data) {
    console.log(data);
    $('#play-button').hide();
    $('#add-instrument-button').hide();
    $('#stop-button').show();
  });
};
