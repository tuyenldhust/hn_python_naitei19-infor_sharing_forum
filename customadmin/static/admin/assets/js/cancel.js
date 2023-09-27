$(document).ready(function() {
  $('#cancel-link').on('click', function(event) {
    console.log('cancel-link clicked');
    event.preventDefault();
    const params = new URLSearchParams(window.location.search);
    if (params.has('_popup')) {
        window.close(); // Close the popup.
    } else {
        window.history.back(); // Otherwise, go back.
    }
  });
});
