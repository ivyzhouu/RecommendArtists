// TasteDive API and endpoint
// alternative key: "280012-Booksand-1ZFHAWKT";
const API_KEY_TASTEDIVE = "324611-Jane-TH6MQQ3R";
const ENDPOINT_TASTEDIVE = "https://tastedive.com/api/similar";

// YouTube API and endpoint
const API_KEY_YOUTUBE = "AIzaSyDf9VtvE5wTSJyzYAfmWV6GJd_vzSa3r2w";
const ENDPOINT_YOUTUBE = "https://www.googleapis.com/youtube/v3/search";
const YOUTUBE_WATCH_VID = "https://www.youtube.com/watch?v=";

const MY_DATA = {
	tastedive: null,
	youtube: []
};

function displaySearchResults() {
	// Create empty string. Will populate the string with HTML markup with the data from MY_DATA.tastedive and MY_DATA.youtube
	let htmlString = "";

	// MY_DATA.tastedive contains two arrays.
	// Create tempArr for the TasteDive arrays to make looping easier by concatenating the Info and Results arrays.
	let tempInfoArr = MY_DATA.tastedive.Similar.Info;
	let tempResultsArr = MY_DATA.tastedive.Similar.Results;
	let tempArrTD = tempInfoArr.concat(tempResultsArr);

	// Variables will contain data from the YouTube API.
	// let ytVideoId;
	let ytThumbNail;
	let ytImgAlt;

	for (let i = 0; i < tempArrTD.length; i++) {
		// ytVideoId and ytThumbNail will be assigned to the appropriate
		// values from MY_DATA.youtube JSON data.
		// The values will be used for the YouTube video link, thumbnail, and alt.

		ytVideoId = MY_DATA.youtube[i].items[0].id.videoId;
		ytThumbNail = MY_DATA.youtube[i].items[0].snippet.thumbnails.medium.url;
		ytImgAlt = MY_DATA.youtube[i].items[0].snippet.title;

		htmlString +=
			`<div class="container-fluid p-0">
				<div class="row no-gutters">
					<div class="col-lg-8 order-lg-1 my-auto showcase-text">
						<h2>${tempArrTD[i].Name}</h2>
						<p class="lead mb-0">${tempArrTD[i].wTeaser}</p>
						<br>
						<p>
							<a href="${tempArrTD[i].wUrl}" target="_blank">Wiki page</a>
						</p>	
					</div>		
					<div class="col-lg-4 order-lg-1 showcase-img">	
						<a href="${tempArrTD[i].yUrl}" target="_blank">
							<img style="padding-top: 10rem" src="${ytThumbNail}" alt="${ytImgAlt}">
						</a>
					</div>
				</div>
			</div>`;
	}

	$(".js-results").html(htmlString);
}

function createArrNamesFromTasteDive() {
	// Create empty array.
	let myArr = [];

	// Loop through MY_DATA.tastedive.Similar.Info array
	// and MY_DATA.tastedive.Similar.Results array.
	// Push the Name key from each element into myArr
	let infoArr = MY_DATA.tastedive.Similar.Info;
	let resultsArr = MY_DATA.tastedive.Similar.Results;

	infoArr.forEach(elem => {myArr.push(elem.Name);} );
	resultsArr.forEach(elem => {myArr.push(elem.Name);} );

	return myArr;
}

function getDataYouTubeAPI() {
	// check if any results were returned for the query in the Results array
	// for the TasteDive API (check the length of the Results array)
	let arrResultsTD = MY_DATA.tastedive.Similar.Results;

	if (arrResultsTD.length === 0) {
		$(".js-results").html(

			 `<div class="container-fluid p-0 js-single-result">
				<div class="row no-gutters">
					<div class="col-lg-8 order-lg-1 my-auto showcase-text">
						<p>There are no results for this query.</p>
						<p>Please try again.</p>
					</div>
				</div>
			</div>`
		);

		// Do NOT perform getJSON() for YouTube API.
		// return to exit this function.
		return undefined;
	}

	// Call createArrNamesFromTasteDiveAPI() to create an array of Names from the TasteDive API call
	let arrNames = createArrNamesFromTasteDive();

	// Empty the array in MY_DATA.youtube in case
	// there are previous results
	MY_DATA.youtube = [];

	// For each element in arrNames, keep track of the promise
	// for the getJSON call. Below, will use Promise.all() on arrName which will then call displaySearchResults()
	let promises = []; // keep track of all promises

	arrNames.forEach(function (elem, index) {
		// arrNames contains an array of string Names from the TasteDive API.
		// each elem string Name will serve as the query search term for the getJSON to the YouTube API

		let dataYouTubeAPI = {
			part: "snippet", // part: "snippet" required by YouTube data API
			key: API_KEY_YOUTUBE,
			q: elem + " artist mv", // the element, it"s a string name

			// get 1 result for each element
			maxResults: 1
		};


		// use getJSON for each element
		let req = $.getJSON(ENDPOINT_YOUTUBE, dataYouTubeAPI, function (data) {
			MY_DATA.youtube.push(data);
		});

		promises.push(req);

	});

	// When all the promises in the promises array are fulfilled, call displaySearchResults().
	Promise.all(promises).then(function () {
		displaySearchResults();
	});

}

function getDataTasteDiveAPI(searchTerm) {
	// data sent with $.ajax() to TasteDive
	let dataTasteDiveAPI = {
		k: API_KEY_TASTEDIVE,
		q: searchTerm,
		type: "music",
		limit: 5,
		info: 1 // extra, verbose=1
	};

	// .ajax() call for TasteDive API
	$.when(
	  $.ajax({
		  type: "GET",
		  url: ENDPOINT_TASTEDIVE,

		  jsonp: "callback", // get around CORS
		  dataType: "jsonp", // get around CORS
		  data: dataTasteDiveAPI, // variable defined above

		  success: function (data) {
		  	// store returned JSON data in object MY_DATA.tastedive
		   	MY_DATA.tastedive = data;
		  }
		})
	).then(function () {
		// wait to get JSON data from TasteDive API before
		// calling getDataYouTubeAPI
	 	getDataYouTubeAPI();
	});
}

function watchSubmit() {
  $(".submitSearch").on("submit", function (event) {
    event.preventDefault();
    
		let queryTarget = $(this).find("#search"); // input field
		let queryTerm = queryTarget.val(); // get the search term
		
		queryTarget.val(""); // empty search field

    getDataTasteDiveAPI(queryTerm); // function call
  });
}

$(watchSubmit);

/////////