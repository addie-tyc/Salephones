function render_products(data) {
    let productsDiv = document.querySelector('#phone-table')

    let products = data.phone_table
    let newHead = document.createElement('div')
    newHead.className = "products"
    newHead.innerHTML = `<div class="row my-border-bottom">
                            <div class="col text-center">價格</div>
                            <div class="col-4 text-center">配件</div>
                            <div class="col text-center">來源</div>
                            <div class="col text-center">建立日期</div>
                         </div>`
    productsDiv.appendChild(newHead)

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
    let phone = data.phone
    let graph = data.phone_graph
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
    data = [avg, avg_low, avg_high, new_price, avg_price_30]
    Plotly.newPlot('phone-graph', data, layout);
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
    render_products(data)
    }
)