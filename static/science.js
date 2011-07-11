var shJQuery = jQuery.noConflict(true);

function addInstitute() {
  hide_addInstitutesSubmit();
  var institute_name_value = document.getElementById('institute_name').value;
  var institute_desc_value = document.getElementById('institute_desc').value;
  var institute_addr_value = document.getElementById('institute_addr').value;
  var institute_host_name_value = document.getElementById('institute_host_name').value;
  var institute_host_email_value = document.getElementById('institute_host_email').value;

  var post_data = { institute_name: institute_name_value, 
                    institute_desc: institute_desc_value,
                    institute_addr: institute_addr_value,
                    institute_host_name: institute_host_name_value,
                    institute_host_email: institute_host_email_value };

  shJQuery.ajax({
    url: "/addInstitutes",
    type: "POST",
    contentType: "application/x-www-form-urlencoded",
    data: (post_data),

    error: function(jqXHR, textStatus, errorThrown) {
      show_addInstitutesSubmit();
    },

    success: function(data, textStatus, jqXHR) {
    },

    complete: function(jqXHR, textStatus) {
      show_addInstitutesSubmit();
    },
  });

}


function approve_add_institute(request_id, approved_val) {
  shJQuery.ajax({
    url: "/approveAddInstitutes",
    type: "POST",
    contentType: "application/x-www-form-urlencoded",
    data: ({approved: approved_val, request: request_id}),

    error: function(jqXHR, textStatus, errorThrown) {
    },

    success: function(data, textStatus, jqXHR) {
    },

    complete: function(jqXHR, textStatus) {
      window.location.reload();
    },
  });
}


function show_addInstitutesSubmit() {
  var addInstitutesSubmit_div = document.getElementById('addInstitutesSubmit');
  var addInstitutesInProgress_div = document.getElementById('addInstitutesInProgress');
  addInstitutesSubmit_div.style.display = '';
  addInstitutesInProgress_div.style.display = 'none';
}

function hide_addInstitutesSubmit() {
  var addInstitutesSubmit_div = document.getElementById('addInstitutesSubmit');
  var addInstitutesInProgress_div = document.getElementById('addInstitutesInProgress');
  addInstitutesSubmit_div.style.display = 'none';
  addInstitutesInProgress_div.style.display = '';
}


