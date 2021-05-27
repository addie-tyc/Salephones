function render_products(data) {
    let productsDiv = document.querySelector('.products')

    let products = data.phone_table

    for (var i = 0; i < products.length; i += 1) {
        let newPost = document.createElement('div')
        let d = products[i]
        newPost.className = "product"
        newPost.innerHTML = `<a href="${d.link}" class="link-reset">
                                <div class="row my-border-bottom justify-content-md-center">
                                    <div name="price" class="col text-center">${d.price}</div>
                                    <div name="box" class="col-5 ">${d.box}</div>
                                    <div name="source" class="col text-center">${d.source}</div>
                                    <div name="created_at" class="col text-center">${d.created_at.replace('T', ' ').replace('Z', '')}</div>
                                </div>
                             </a>`
        productsDiv.appendChild(newPost)
        }
}

function draw_phone_graph (data) {
    var phone = data.phone
    var graph = data.phone_graph
    var avg = {
        x: graph.date, 
        y: graph.old_price, 
        line: {color: 'rgb(0,100,150)'}, 
        name: "Second-hand Avg Price", 
        type: "scatter"
      };
      
    var avg_low = {
        x: graph.date, 
        y: graph.min_price,
        fill: "tonexty", 
        fillcolor: 'rgba(68, 68, 68, 0.2)', 
        line: {color: "transparent"}, 
        marker: {color: "#444"},
        name: "Min", 
        showlegend: false, 
        type: "scatter"
    };
      
    var avg_high = {
        x: graph.date, 
        y: graph.max_price,
        fill: "tonexty", 
        fillcolor: 'rgba(68, 68, 68, 0.2)', 
        line: {color: "transparent"}, 
        marker: {color: "#444"},
        name: "Max", 
        showlegend: false, 
        type: "scatter"
    };

    var new_price = {
        x: graph.date, 
        y: graph.new_price, 
        line: {color: 'rgb(200,100,150)'}, 
        name: "Buy a New One Today", 
        type: "scatter"
      };

    var avg_price_30 = {
        x: graph.date, 
        y: graph.avg_price_30, 
        line: {color: 'rgb(100,200,150)'}, 
        name: "Second-hand Avg Price <br> within 30 Days", 
        type: "scatter"
    };

    var layout = {
        title: {
            text:`${phone} Price History`,
        },
        width: 648,
        height: 400
    }
    var data = [avg, avg_low, avg_high, new_price, avg_price_30]
    Plotly.newPlot('phone-graph', data, layout);
}

function draw_storage_graph (data) {
    var phone = data.phone
    var graph = data.storage_graph
    let storages = Object.keys(graph)
    console.log(storages)
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

    var new_price = {
        x: graph.date, 
        y: graph.new_price, 
        line: {color: 'rgb(200,100,150)'}, 
        name: "Buy a New One Today", 
        type: "scatter"
      };

    var avg_price_30 = {
        x: graph.date, 
        y: graph.avg_price_30, 
        line: {color: 'rgb(100,200,150)'}, 
        name: "Second-hand Avg Price <br> within 30 Days", 
        type: "scatter"
    };

    var layout = {
        title: {
            text:`${phone} Price History of different storage`,
        },
        width: 648,
        height: 400
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
        let newP = document.createElement('p')
        newP.textContent = "參考更多："
        linkDiv.appendChild(newP)
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
            newLink.innerHTML = `<a href="/smartphone-smartprice/detail/${link_title}/${s}" class="link-reset">${title} ${s}GB</a>`
            newRow.appendChild(newLink)
        }
    }
    linkDiv.appendChild(newRow)
    
}


url_array = window.location.href.split("/")
storage = url_array.pop()
title = url_array.pop().split("-").join("+")


fetch(`/api/v1/detail?title=${title}&storage=${storage}`,{
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
    draw_phone_graph(data)
    draw_storage_graph(data)
    render_products(data)
    add_storage_link(data)
    }
)