// index.js: Read and visualize a JSON given from student classifier

var nodes;
var edges;
var nodeCount = 0;

$('#visu-image').click(function() {
    printToFile(document.getElementById("visualize-json"));
})

function draw() {
    var obj = JSON.parse(content);
    nodeCount = 0;

    for(var i=0;i<students.length;i++) {
        $('#st-table tr').append($("<td>"));
        $('#st-table thead tr>td:last').html(students[i]);
    }

    var chart_config = {
        chart: {
            container: "#visualize-json",
            nodeAlign: "CENTER",
            rootOrientation: "WEST",
            connectors: {
                type: 'straight'
            },
            node: {
                HTMLclass: 'nodeExample1'
            }
        },
        nodeStructure: {
            HTMLclass: 'root-blue',
            text: {
                name: "Root Object"
            },
            children: buildNodes(obj)
        }
    };
    new Treant( chart_config );
};

function buildNodes(obj) {
    if(Array.isArray(obj)) {
        var ret_obj = [];
        /*
        for(var i = 0; i < obj.length; i++) {
            var row = document.getElementById("st-table").insertRow(-1);
            row.insertCell(0).innerHTML = obj[i].name;
            for(var j = 0; j < obj[i].keys.length; j++) {
                var cell = row.insertCell(j + 1);
                if(obj[i].keys[j] == true) {
                    cell.innerHTML = '<span class="text-yes">Y</span>';
                }
                else {
                    cell.innerHTML = '<span class="text-no">N</span>';
                }
                
            }
            ret_obj.push({
                text: {
                    name: obj[i].name
                },
                HTMLclass: "leaf"
            })
        }
        */
        return ret_obj;
    }
    else {
        var ret_obj = [];
        for(key in obj) {
            var html_cls = "";
            if(key == "True")
                html_cls = "blue";
            else if(key == "False")
                html_cls = "red";
            var new_obj = {
                text: {
                    name: key
                },
                HTMLclass: html_cls,
                children: buildNodes(obj[key])
            };
            ret_obj.push(new_obj);
        }
        return ret_obj;
    }
}

//Creating dynamic link that automatically click
function downloadURI(uri, name) {
    var link = document.createElement("a");
    link.download = name;
    link.href = uri;
    link.click();
    //after creating link you should delete dynamic link
    //clearDynamicLink(link); 
}

//Your modified code.
function printToFile(div) {
    $("#text-imgloading").toggle();
    html2canvas(div, {
        onrendered: function (canvas) {
            $("#text-imgloading").toggle();
            var myImage = canvas.toDataURL("image/png");
            //create your own dialog with warning before saving file
            //beforeDownloadReadMessage();
            //Then download file
            downloadURI("data:" + myImage, "yourImage.png");
        }
    });
}
