function render_user_info(user_info) {
    let profileDiv = document.querySelector('#profile')
    var newDiv = document.createElement('div')
    // newDiv.className = "justify-content-md-center"
    newDiv.innerHTML = `<div>使用者名稱: ${user_info.username}</div>
                        <div>電子信箱: ${user_info.email}</div>`
    profileDiv.appendChild(newDiv)
}

function render_post(data) {
    let postDiv = document.querySelector('#sale-post')
    let sale_post =  data.sale_post
    var newDiv = document.createElement('div')
    newDiv.className = "row text-center"
    if (sale_post.length > 0) {
        newDiv.innerHTML = `<div name="image" class="col-5 text-center"></div>
        <div name="title" class="col text-center">商品名稱</div>
        <div name="price" class="col text-center">價格</div>
        <div name="created_at" class="col text-center">上架時間</div>`
    } else {
        newDiv.innerHTML = `<div class="col text-center">目前無資料</div>`
    }
    postDiv.appendChild(newDiv)
    for (var i = 0; i < sale_post.length; i += 1) {
        var newA = document.createElement('a')
        newA.className = "link-reset"
        newA.href = `/post/${sale_post[i].id}`
        var img = sale_post[i]["images"].split(',')[0]
        newA.innerHTML = `<div class="row post v-center">
                                <div name="image" class="col-5 text-center"><img src=${img}></div>
                                <div name="title" class="col text-center">${sale_post[i].title}</div>
                                <div name="price" class="col text-center">${sale_post[i].price}</div>
                                <div name="created_at" class="col text-center">${sale_post[i].created_at.replace('T', ' ').replace('Z', '')}</div>
                            </div>`
        postDiv.appendChild(newA)
    }
}


fetch(`/api/v1/profile`,{
    method: 'GET',
})
.then(response => {
    // console.log(response.json())
    return response.json()
})
.then(data => {
    render_user_info(data.user_info)
    render_post(data)
    }
)