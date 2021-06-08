function filter_brand(brand) {
    let products = $('.products-by-brand')
    let button = $(`#${brand}-button`)

    if (button.css('backgroundColor') === "rgb(54, 79, 125)") {
        for (var i = 0; i < products.length; i += 1) {
            products[i].style = ''
            button.css("backgroundColor", "beige")
            button.css("color", "#212529")
        }
    } else {
        for (var i = 0; i < products.length; i += 1) {
            if (products[i].id === brand) {
                products[i].style = ''
                button.css("backgroundColor", "#364F7D")
                button.css("color", "#fff")
            } else {
                products[i].style = 'display:none'
                $(`#${products[i].id}-button`).css("backgroundColor", "beige")
                $(`#${products[i].id}-button`).css("color", "#212529")
                }
            }
    }
    
}

function render_products(data) {
    let productsDiv = document.querySelector('.products')
    let buttonsDiv = document.querySelector('.buttons')

    let products = data.products
    let brands = Object.keys(products)

    let newRow = document.createElement('div')
    newRow.className = "row"

    for (var i = 0; i < brands.length; i += 1) {
        let newBrand = document.createElement('div')
        let brand = brands[i]

        let newButton = document.createElement('button')
        newButton.innerHTML = `${brand}`
        newButton.id = `${brand}-button`
        newButton.type = 'button'
        newButton.className = "col text-center border-pilled btn"
        newButton.setAttribute('onclick', "filter_brand('"+brand+"')")
        newRow.appendChild(newButton)

        newBrand.id = `${brand}`
        newBrand.className = "products-by-brand"
        newBrand.innerHTML = `<div class="row">
                                <div class="col-3"><img class="brand-logo" src="https://aws-bucket-addie.s3-ap-northeast-1.amazonaws.com/smartphone/brand_logos/logo_${brand.toLowerCase()}.svg"</div>
                                <div class="col-3"></div>
                                <div class="col-3"></div>
                             </div>`
        var lst = products[brand]
        for (var j in lst) {
            d = lst[j]
            let newProduct = document.createElement('a')
            if (d.title.includes("+")) {
                var link_title = d.title.replace("+", "plus")
            } else {
                var link_title = d.title
            }
            newProduct.className = "link-reset"
            newProduct.href = `/detail/${link_title.split(" ").join("-")}/${d.storage.replace("GB", "")}`
            if (d.title === lst[lst.length-1].title) {
                newProduct.innerHTML = `<div class="row my-border-bottom d-flex last-row justify-content-center">
                                            <div name="title" class="col-5 fs-4 text-center">${d.title}</div>
                                            <div name="storage" class="col-3 fs-5 text-center">${d.storage}</div>
                                            <div name=new-price class="col-3 fs-5 text-center">
                                                <div class="row">新機均價： ${d.new_price}</div>
                                                <div class="row last-column-bottom">二手均價： ${d.old_price}</div>
                                            </div>
                                        </div>`
            } else {
                newProduct.innerHTML = `<div class="row my-border-bottom d-flex justify-content-center">
                                            <div name="title" class="col-5 fs-4 text-center">${d.title}</div>
                                            <div name="storage" class="col-3 fs-5 text-center">${d.storage}</div>
                                            <div name=new-price class="col-3 fs-5 text-center">
                                                <div class="row">新機均價： ${d.new_price}</div>
                                                <div class="row last-column-bottom">二手均價： ${d.old_price}</div>
                                            </div>
                                        </div>`
            }   
            newBrand.appendChild(newProduct);
            }
        buttonsDiv.appendChild(newRow)
        productsDiv.appendChild(newBrand)
        }
}

fetch("/api/v1/home",{
    method: 'GET',
})
.then(response => {
    // console.log(response.json())
    return response.json()
})
.then(data => {
    console.log(data)
    render_products(data)
    }
)