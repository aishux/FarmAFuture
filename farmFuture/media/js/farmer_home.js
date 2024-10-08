var current_user_account = ""
var token_contract = ""
var operations_contract = ""
const address_token_contract = "0x09BAF90d7E050f282bDa3fe55a0F5726fE629D51"
const address_farm_operations = "0x7d86bbFD06Af97782bc170B4800ef4cA14aa5C8b"

const web = new Web3("https://rinkeby.infura.io/v3/384b2420ae804f5ca4b5d6aa630f3c7b")


$.ajax({
    url: "https://api-rinkeby.etherscan.io/api?module=contract&action=getabi&address=0x09BAF90d7E050f282bDa3fe55a0F5726fE629D51&apikey=39MRYT8W4D35AH26BJZVGQ1KK19SR5XWXG",
    dataType: "json",
    success: function (data) {
        token_contract = new web.eth.Contract(JSON.parse(data.result), address_token_contract)
        localStorage.setItem('token_contract', JSON.stringify([JSON.parse(data.result), address_token_contract]))
    }
});

$.ajax({
    url: "https://api-rinkeby.etherscan.io/api?module=contract&action=getabi&address=0x7d86bbFD06Af97782bc170B4800ef4cA14aa5C8b&apikey=39MRYT8W4D35AH26BJZVGQ1KK19SR5XWXG",
    dataType: "json",
    success: function (data) {
        operations_contract = new web.eth.Contract(JSON.parse(data.result), address_farm_operations)
        getAllGoods()
        localStorage.setItem('operations_contract', JSON.stringify([JSON.parse(data.result), address_farm_operations]))
    }
});

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