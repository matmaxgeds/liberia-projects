// SET UP DATES
var earliest_activity_date = new Date(activity_dates['earliest']);
var latest_activity_date = new Date(activity_dates['latest']);
$(".date-select .min-date").text(earliest_activity_date.getFullYear());
$(".date-select .max-date").text(latest_activity_date.getFullYear());
var dateSlider = $('#date-selector').slider({
  id: 'slider2',
  min: earliest_activity_date.getTime(),
  max: latest_activity_date.getTime(),
  value: [earliest_activity_date.getTime(), latest_activity_date.getTime()],
  formatter: function(value) {
    if (value.length == 2) {
      date_from = new Date(value[0]).toLocaleDateString();
      date_to = new Date(value[1]).toLocaleDateString();
      return date_from + ' – ' + date_to;
    }
    date = new Date(value);
    return 'Current date: ' + date.toLocaleDateString();
  }
});

// PROJECTS
var updateProjects = function(projects) {
  // Render projects template
	var projects_template = $('#projects-template').html();
	Mustache.parse(projects_template);
	var rendered = Mustache.render(projects_template, projects);
	$('#projects-data').html(rendered);
  $("#activities_count").text(projects.activities.length+" found");
  $.tablesorter.themes.bootstrap = {
    caption      : 'caption',
    header       : 'bootstrap-header',
    iconSortNone : 'bootstrap-icon-unsorted',
    iconSortAsc  : 'glyphicon glyphicon-chevron-up',
    iconSortDesc : 'glyphicon glyphicon-chevron-down',
  };
  $("#projectsList").tablesorter( {
      sortList: [[3,1],[1,0],[0,0]],
      theme : "bootstrap",
      widthFixed: true,
      headerTemplate : '{content} {icon}',
      widgets : [ "uitheme"]
  } );
}
var projects_template;
var projectData;
var queryProjectsData = function() {
  // Check dates
  var values = $("#date-selector").slider("getValue");
  var selected_earliest_activity_date = new Date(values[0]);
  var selected_latest_activity_date = new Date(values[1]);
  var data = {}
  var query = ""
  var fv_data = $.map($(".filter-select"),
        function(d) {
          return {"id": d.id, "value": d.value}
       });

  if (
      (values.length==2) &&
      ((earliest_activity_date.toString()!=selected_earliest_activity_date.toString()) ||
       (latest_activity_date.toString()!=selected_latest_activity_date.toString()))
    ) {
      fv_data.push({
        "id": "earliest_date", "value": selected_earliest_activity_date.toJSON()
          })
      fv_data.push({
        "id": "latest_date", "value": selected_latest_activity_date.toJSON()
      })
  };

  var filtersApplied = false;
  $(fv_data).each(function(i, f) {
    data[f["id"]] = f["value"]
    if (i == 0) { query+= "?" 
    } else { query+= "&" }
    if (f["value"] != "all") { filtersApplied=true; }
    query += f["id"] + "=" + f["value"];
  });
  makeFiltersApplied(filtersApplied);
  $("#activities_count").text("loading...");
  $("#projectsList").html('<p class="lead">Loading data, please wait... <span class="glyphicon glyphicon-refresh loader" aria-hidden="true"></span></p>');

  $.get("/api/activities/", data, function(resultdata) {
    updateProjects(resultdata);
  });
  $("#download_excel").attr("href", "/api/activities_filtered.xlsx" + query);
  window.location.hash = query;
}
$(document).on("change", ".filter-select", function(e) {
  queryProjectsData();
});
$(document).on("slideStop", "#date-selector", function(e) {
  queryProjectsData();
  values = e.value;
  var min_date = new Date(values[0]);
  var max_date = new Date(values[1]);
  $(".date-select .min-date").text(min_date.getFullYear());
  $(".date-select .max-date").text(max_date.getFullYear());
});

function makeFiltersApplied(applied) {
  if (applied == true) {
    $("#filtersAppliedLabel").html('<span class="label label-danger"><a href="">Reset filters</a></span>'
      ).delay("500").fadeTo("fast", 1).fadeTo("100", 0.2).fadeTo("fast", 1);
  } else {
    $("#filtersAppliedLabel").fadeOut("fast").next().html("");
  }
}
$(document).on("click", "#filtersAppliedLabel a", function(e) {
  e.preventDefault();
  $(".filter-select").val("all");
  makeFiltersApplied(false);
  queryProjectsData();
});
// Make results persistent using URL hash
var url = document.location.toString();
if (url.match('#')) {
    params = url.split("#?")[1].split("&");
    console.log(params);
    var filtersApplied=false;
    params.forEach(function(param) {
      var key = param.split("=")[0];
      var value = param.split("=")[1];
      $(".form-activity-filters #"+key).val(value);
      if (value != "all") {
        filtersApplied=true;
      }
    });
    makeFiltersApplied(filtersApplied);
    window.scrollTo(0, 0);
}
queryProjectsData()
