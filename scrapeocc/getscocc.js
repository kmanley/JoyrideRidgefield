var system = require('system');
var args = system.args;
var page = require("webpage").create(),
    url = args[1]
//console.log(url)

function onPageReady() {
    var htmlContent = page.evaluate(function () {
        return document.documentElement.outerHTML;
    });

   //console.log(htmlContent);
   var regExp = new RegExp("the class you requested is full", "gi");
   var isFull = (htmlContent.match(regExp) || []).length
   if (isFull > 0) {
	   console.log(-1)
   } else {
	   var regExp = new RegExp("seat taken", "gi");
       console.log((htmlContent.match(regExp) || []).length);
   }

    phantom.exit();
}

page.open(url, function (status) {
    function checkReadyState() {
        setTimeout(function () {
            var readyState = page.evaluate(function () {
                return document.readyState;
            });

            if ("complete" === readyState) {
                onPageReady();
            } else {
                checkReadyState();
            }
        });
    }

    checkReadyState();
});
