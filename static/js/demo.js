

//map
function GetMap() {
  var map = new Microsoft.Maps.Map('#myMap', {
      credentials: "AsB0G6V1EsHxenhCcPOu1CI5XVqwuFW3naBCgOA-F_oU-A0Mcok-i7LT_fVR5E1_"
  });

  //Request the user's location
  navigator.geolocation.getCurrentPosition(function (position) {
      var loc = new Microsoft.Maps.Location(
          position.coords.latitude,
          position.coords.longitude);

      //Add a pushpin at the user's location.
      var pin = new Microsoft.Maps.Pushpin(loc);
      map.entities.push(pin);

      //Center the map on the user's location.
      map.setView({ center: loc, zoom: 15 });
  });
}


//

$(document).ready(function() {
    $('body').materialScrollTop({
        revealElement: 'header',
        revealPosition: 'bottom',
        onScrollEnd: function() {
            console.log('Scrolling End');
        }
    });
});


(function ($) {
    'use strict';

    var alime_window = $(window);



    if ($.fn.owlCarousel) {
        var instagramFeedSlider = $('.instragram-feed-area');
        instagramFeedSlider.owlCarousel({
            items: 6,
            loop: true,
            autoplay: true,
            smartSpeed: 1000,
            autoplayTimeout: 3000,
            responsive: {
                0: {
                    items: 2
                },
                576: {
                    items: 3
                },
                768: {
                    items: 4
                },
                992: {
                    items: 5
                },
                1200: {
                    items: 6
                }
            }
        })
    }


})(jQuery);


//load
if (typeof(Storage) !== "undefined"){
    if (localStorage.pagecount)
    {
    localStorage.pagecount=Number(localStorage.pagecount) +1;
    }
  else
    {
    localStorage.pagecount=1;
    }
  // document.write("Visits: " + localStorage.pagecount + " time(s).");
  document.getElementById("load").innerHTML = "Visits: " + localStorage.pagecount + " time(s).";
}else{
    document.getElementById("load").innerHTML = "抱歉！您的浏览器不支持 Web Storage";
}



jQuery(document).on('copy', function(e)
	{
	  var selected = window.getSelection();
	  var selectedText = selected.toString().replace(/\n/g, '<br>');  // Solve the line breaks conversion issue
	  var pageInfo = '<br>---------------------<br>©All rights reserved by Huang Siyuan<br>' 
	                        + 'For commercial reprints, please contact the author for authorization. <br>For non-commercial reprints, please indicate the source.<br>';
	  var copyHolder = $('<div>', {id: 'temp', html: selectedText + pageInfo, style: {position: 'absolute', left: '-99999px'}});
	    
	  $('body').append(copyHolder);
	  selected.selectAllChildren( copyHolder[0] );
	  window.setTimeout(function() {
	      copyHolder.remove();
	  },0);
	});

