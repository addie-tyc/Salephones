function render_products(data) {

    let productsDiv = document.querySelector('tbody')

    let products = data.phone_table

    for (var i = 0; i < products.length; i += 1) {
        let newPost = document.createElement('tr')
        let d = products[i]
        newPost.className = "product row my-border-bottom justify-content-md-center"
        if (d.source === "native") {
            d.link = `/post/${d.id}` 
        }
        newPost.setAttribute('onclick', `window.open('${d.link}')`);
        newPost.innerHTML = `
                                <td name="price" class="col text-center">${d.price}</td>
                                <td name="box" class="col-5">${d.box}</td>
                                <td name="source" class="col text-center">
                                    <img class="source-img" src="https://aws-bucket-addie.s3.ap-northeast-1.amazonaws.com/smartphone/source_logo/${d.source}.png">
                                </td>
                                <td name="created_at" class="col text-center">${d.created_at.replace('T', ' ').replace('Z', '')}</td>
                             `
        productsDiv.appendChild(newPost)
        }
    let phone_table = document.querySelector('#phone-table')
    sorttable.makeSortable(phone_table);
}

function draw_phone_graph (data) {
    var phone = data.phone
    var graph = data.phone_graph
    var avg = {
        x: graph.date, 
        y: graph.old_price, 
        line: {color: 'rgb(0,100,150)'}, 
        name: "二手均價", 
        type: "scatter"
      };
      
    var avg_low = {
        x: graph.date, 
        y: graph.min_price,
        fill: "tonexty", 
        fillcolor: 'rgba(68, 68, 68, 0.2)', 
        line: {color: "transparent"}, 
        marker: {color: "#222"},
        name: "當日最低價", 
        showlegend: false, 
        type: "scatter"
    };
      
    var avg_high = {
        x: graph.date, 
        y: graph.max_price,
        fill: "tonexty", 
        fillcolor: 'rgba(68, 68, 68, 0.2)', 
        line: {color: "transparent"}, 
        marker: {color: "#222"},
        name: "當日最高價", 
        showlegend: false, 
        type: "scatter"
    };

    var new_price = {
        x: graph.date, 
        y: graph.new_price, 
        line: {color: 'rgb(200,100,150)'}, 
        name: "新機價", 
        mode: "lines"
      };

    var avg_price_30 = {
        x: graph.date, 
        y: graph.avg_price_30, 
        line: {color: 'rgb(100,200,150)'}, 
        name: "30 日內二手均價",
        mode: "lines" 
    };

    var layout = {
        title: {
            text:`${phone} 歷史價格走勢`,
        },
        width: screen.width*0.44,
        height: screen.width*0.44*0.5625
    }
    var data = [avg, avg_low, avg_high, new_price, avg_price_30]
    Plotly.newPlot('phone-graph', data, layout);
}

function draw_storage_graph (data) {
    var phone = data.phone
    var graph = data.storage_graph
    let storages = Object.keys(graph)
    var data = [] // storages.length
    for (var i = 0; i < storages.length; i += 1) {

        s = storages[i]

        if (phone.includes(s)) {
            var color = 'rgb(200,100,150)'
        } else {
            var color = 'rgb(0,100,150)'
        }
    

        var avg = {
            x: graph[s].date, 
            y: graph[s].old_price, 
            line: {color: color}, 
            name: s, 
            type: "scatter"
          };
        data.push(avg)

    }

    var layout = {
        title: {
            text:`${phone} 不同容量歷史價格走勢`,
        },
        width: screen.width*0.44,
        height: screen.width*0.44*0.5625
    }
    Plotly.newPlot('storage-graph', data, layout);
}

function add_storage_link(data) {
    let linkDiv = document.querySelector('#storage-link')
    var graph = data.storage_graph
    let title = data.title
    let storage = data.storage
    let storages = Object.keys(graph)
    if (storages.length > 1) {
        let newDiv = document.createElement('div')
        newDiv.className = "word-div"
        newDiv.textContent = "參考更多："
        linkDiv.appendChild(newDiv)
    }
    let newRow = document.createElement('div')
    newRow.className = "row"
    for (var i = 0; i < storages.length; i += 1) {

        var newLink = document.createElement('div')
        newLink.className = "col text-center"
        s = storages[i]

        if (!(storage.includes(s))) {
            if (title.includes("+")) {
                var link_title = title.replace(" ", "-").replace("+", "plus")
            } else {
                var link_title = title.replaceAll(" ", "-")
            }
            newLink.innerHTML = `<a href="/detail/${link_title}/${s}" class="link-reset">${title} ${s}GB</a>`
            newRow.appendChild(newLink)
        }
    }
    linkDiv.appendChild(newRow)
    
}



function render_comments(data) {
    let commDiv = document.querySelector('#comments-div')
    let commWord = document.querySelector('#comments-word')
    let keys = Object.keys(data)
    if (keys.length > 0) {
        commWord.innerHTML = `<h3 class="">怕踩雷嗎？看用過的人怎麼說</h3>`
        // <h4>用戶回饋</h4>
        commDiv.innerHTML = `
                             <div id=comments-graph class="clear-float text-center board">
                             </div>`
        if (data["doc"]["score"] > 0) {
            var col = 'rgb(200,100,150)'
            var senti = [{
                type: 'bar',
                x: [data["doc"]["score"]],
                y: ["score"],
                line: {color: col}, 
                width: [1],
                orientation: 'h'
            }]; 
        } else if (data["doc"]["score"] < 0) {
            var col = 'rgb(0,100,150)'
            var senti = [{
                type: 'bar',
                x: [data["doc"]["score"]],
                y: ["score"],
                line: {color: col}, 
                width: [1],
                orientation: 'h'
            }];  
        } else {
            var col = 'rgb(200,100,150)'
            var senti = [{
                type: 'scatter',
                x: [data["doc"]["score"]],
                y: ["score"],
                line: {color: col},
                marker: { size: 12 } 
            }];
        }
        var layout = {
            title: "網友評價情緒",
            width: 648,
            height: 200,
            xaxis: {
                range: [-1, 1],
                },
            yaxis:{visible: false
            }
        }
        Plotly.newPlot('comments-graph', senti, layout);

        
        for (var i = 1; i < keys.length; i += 1) {
    
            if (keys[i] === "goods") {
                var newDiv = document.createElement('div')
                newDiv.className = `comments board float-start`
                newDiv.innerHTML = "<h5>網友正評</h5>"
                var newUl = document.createElement('ul')
                for (var j = 1; j < data[keys[i]].length; j += 1) {
                    var newLi = document.createElement('li')
                    newLi.textContent = data[keys[i]][j]
                    newUl.appendChild(newLi)
                }
                newDiv.appendChild(newUl)
                commDiv.appendChild(newDiv)
            } 
            if (keys[i] === "bads") {
                var newDiv = document.createElement('div')
                newDiv.className = `comments board float-end`
                newDiv.innerHTML = "<h5>網友負評</h5>"
                var newUl = document.createElement('ul')
                for (var j = 0; j < data[keys[i]].length; j += 1) {
                    var newLi = document.createElement('li')
                    newLi.textContent = data[keys[i]][j]
                    newUl.appendChild(newLi)
                }
                newDiv.appendChild(newUl)
                commDiv.appendChild(newDiv)
            }
        }
    }
}

url_array = window.location.href.split("/")
storage = url_array.pop()
title = url_array.pop().split("-").join("+")


fetch(`/api/v1/table?title=${title}&storage=${storage}`,{
    method: 'GET',
})
.then(response => {
    // console.log(response.json())
    return response.json()
})
.then(data => {
    let title = document.createElement('h2')
    title.innerHTML = data.phone
    document.querySelector('#phone-title').appendChild(title)
    render_products(data)
    }
)

fetch(`/api/v1/price-graph?title=${title}&storage=${storage}`,{
    method: 'GET',
})
.then(response => {
    // console.log(response.json())
    return response.json()
})
.then(data => {
    draw_phone_graph(data)
    }
)

fetch(`/api/v1/storage-graph?title=${title}&storage=${storage}`,{
    method: 'GET',
})
.then(response => {
    // console.log(response.json())
    return response.json()
})
.then(data => {
    draw_storage_graph(data)
    add_storage_link(data)
    }
)

fetch(`/api/v1/comments?title=${title}`,{
    method: 'GET',
})
.then(response => {
    // console.log(response.json())
    return response.json()
})
.then(data => {
    render_comments(data)
    }
)