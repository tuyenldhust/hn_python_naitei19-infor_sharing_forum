$(document).ready(function() {

  // If has error, add class to the field
  if ($('.errorlist').length > 0) {
    $('.errorlist').each(function() {
      $(this).addClass('alert alert-danger');
    });
  }

});
