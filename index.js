function search()
{
    var apigClient = apigClientFactory.newClient(); 
    var user_message = document.getElementById('input').value;
    var body = {};
    var params = {q : user_message};
    // var additionalParams = {headers: {'Access-Control-Allow-Origin': '*', 'Content-Type':"application/json", 'timeout':600000}};

    console.log(params, body);

    apigClient.searchGet(params, body).then(function(result){
        /*var data = {}
        var data_array = []
        resp_data  = res.data
        length_of_response = resp_data.length;*/

        console.log('success OK');
        display(result.data.results);
    }).catch(function(result){console.log(result); });
        /*if(length_of_response == 0)
        {
          document.getElementById("displaytext").innerHTML = "No Images Found !!!"
          document.getElementById("displaytext").style.display = "block";

        }

        resp_data.forEach( function(obj) {

            var img = new Image();
            img.src = "https://s3.amazonaws.com/photoboy/"+obj;
            img.setAttribute("class", "banner-img");
            img.setAttribute("alt", "effy");
            document.getElementById("displaytext").innerHTML = "Images returned are : "
            document.getElementById("img-container").appendChild(img);
            document.getElementById("displaytext").style.display = "block";

        }); */
};

function getBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      let encoded = reader.result.replace(/^data:(.*;base64,)?/,'');
      if ((encoded.length % 4) > 0) {
        encoded += '='.repeat(4 - (encoded.length % 4));
      }
      resolve(encoded);
    };
    reader.onerror = error => reject(error);
  });
}


function upload() {
    /*if(fileExt == 'jpg' || fileExt == 'jpeg' || fileExt == 'png'){
      encodedStr = encoded.substring(33, encoded.lastIndexOf('"'));  
    }
    else{
        encodedStr = encoded.substring(32, encoded.lastIndexOf('"'));
    } */

    var file = document.getElementById('upload').files[0];
    var labels = document.getElementById('labels').value;
    const reader = new FileReader();

    var file_data;
    var encoded_image = getBase64(file).then(
      data => {
      console.log(data)
      var apigClient = apigClientFactory.newClient();
      var file_type = file.type + ";base64";
      console.log(file_type)
      var body = data;
      var params = {"filename" : file.name, "labels": labels, "Content-Type": file_type};
      // var additionalParams = {"Access-Control-Allow-Origin": "*"};
      apigClient.uploadPut(params, body).then(function(result){
        console.log('success OK');
        alert ("Photo uploaded successfully!");
      }).catch(function(result){console.log(result);});    
      /* apigClient.uploadPut(params, body , additionalParams).then(function(res){
        if (res.status == 200)
        {
          document.getElementById("upload").innerHTML = "Image uploaded!"
          document.getElementById("upload").style.display = "block";
        }
    }) */
    });

}

function display(res){
  var image = document.getElementById("image");
  while(image.firstChild){
    image.removeChild(image.firstChild);
  }
  console.log(res)
    if(res.length==0){
    image.appendChild(document.createTextNode("No image to display"));
    var oldimage = document.getElementById("oldimage"); 
    document.body.insertBefore(image, oldimage);
    }
    else{
	for (var i = 0; i < res.length; i++) {
	console.log(res[i]);
	var image = document.getElementById("image");
	image.style.display = 'inline'
	var newContent = document.createElement("img");
	newContent.src = res[i];
	newContent.style.padding = "20px";
	newContent.style.height = "200px";
	newContent.style.width = "200px";
	image.appendChild(newContent);
	var oldimage = document.getElementById("oldimage"); 
	document.body.insertBefore(image, oldimage);
	}
  }
}

