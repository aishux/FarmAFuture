const web = new Web3("https://rinkeby.infura.io/v3/384b2420ae804f5ca4b5d6aa630f3c7b")
token_contract_details = JSON.parse(localStorage.getItem("token_contract"))
operations_contract_details = JSON.parse(localStorage.getItem("operations_contract"))
var token_contract = new web.eth.Contract(token_contract_details[0], token_contract_details[1])
var operations_contract = new web.eth.Contract(operations_contract_details[0], operations_contract_details[1])

getAllGoods()

async function getAllGoods() {
    var $main_div = $("#items_container")
    var $row_item = $('<div class="row"></div>')
    farmer_address = $("#farmer_address").text()
    all_goods = await operations_contract.methods.getGoodByFarmer(farmer_address).call()
    for (let index = 0; index < all_goods.length; index++) {
        $row_item.append(`
            <div class="column">
            <div class="card" style="width:250px">
                <img src="${all_goods[index].image_uri}" alt="Mountains" style="width:100%; height:150px;border:1px solid #F0BB62">
                <h3 style="color:#064635">${all_goods[index].name}</h3>
                <p style="color:#519259">${all_goods[index].description}</p>
            </div>
            </div>
        `)

        if (index > 0 && index % 5 == 0 && index != all_goods.length) {
            $main_div.append($row_item)
            $row_item = $('<div class="row"></div>')
        }

    }
    $main_div.append($row_item)
}