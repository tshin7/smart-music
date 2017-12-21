'use strict';

(function () {


})();

$('#ex1').slider({

  formatter: function(value) {
    console.log("asdf");
    console.log(value);
    return 'Current value: ' + value;
  }
});

function handleStartClick() {
  $.get('/start', function(data) {
    console.log(data);
    $('#start-button').prop("disabled", true);
    $('#stop-button').prop("disabled", false);
    $('#add-instrument-button').prop("disabled", false);
  });
};

function handlePlayClick() {
  $.get('/play', function(data) {
    console.log(data);
    $('#play-button').prop("disabled", true);
    //$('#add-instrument-button').prop("disabled", true);
    $('#stop-button').prop("disabled", false);
  });
};

function handleStopClick() {
  $.get('/stop', function(data) {
    console.log(data);
    $('#stop-button').prop("disabled", true);
    $('#play-button').prop("disabled", false);
    $('#add-instrument-button').prop("disabled", false);
  });
};

function handleAddInstrumentClick() {
  $.get('/add-instrument', function(data) {
    console.log(data);
    $('#play-button').prop("disabled", true);
    //$('#add-instrument-button').prop("disabled", true);
    $('#stop-button').prop("disabled", false);
  });
};

function handleResetClick() {
  $.get('/reset', function(data) {
    console.log(data);
    $('#stop-button').prop("disabled", true);
    $('#start-button').prop("disabled", false);
    $('#add-instrument-button').prop("disabled", true);
    // $('#reset-button').prop("disabled", false);
  });
};

function handleRateClick() {
  let rating = $('#ex1').val();
  console.log(rating);
  $('#rating-text').empty();
  $('#rating-text').append('You rated the most recent instrument as: ' + rating);
};
