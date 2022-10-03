function addBill() {
    var inputBillName = document.getElementById('inputBillName').value;
    var inputBillAmount = document.getElementById('inputBillAmount').value;
    console.log(inputBillName);
    console.log(inputBillAmount);


    console.log("hi");

    var inp = document.getElementsByTagName("li");
    let idArr = [];
    let payeesArr = [];
    for (let i = 0; i < inp.length; i++) {
        var element = inp[i];
        var box = element.firstChild
        if (box.checked) {
            console.log(box.id);
            payeesArr.push(element)
            idArr.push(box.id)
        }
    }
    $.ajax({
        url: "/addBill",
        type: "POST",
        data: {idArr:idArr, inputBillName:inputBillName, inputBillAmount:inputBillAmount},
        success: function(data){
            var BillName = document.createElement('tr');
            BillName.innerHTML="<h2>"+ inputBillName + "</h2>";
            document.getElementById('names').appendChild(BillName);
            var individualPayment = (inputBillAmount/idArr.length);
            individualPayment = individualPayment.toFixed(2);
            
            for (let i = 0; i < idArr.length; i++) {
                var element = payeesArr[i];
                var details = document.createElement('tr');
                details.innerHTML="<td>" + element.textContent +"</td> <td>"+ individualPayment +"</td> <td> false </td>"
                BillName.append(details);
            }
            
            
            
        }
    })
    Popup();
}

function myFunction(id){
    console.log(id)

    $.ajax({
        type: "POST",
        url: '/userPaid',
        data: {id:id},
        success: function(data){
            if($('#' + id).is(":checked"))
                alert("Setting payee status for as paid. Awaiting payer confirmation.")
        }
    })
}