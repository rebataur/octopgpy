var cte = {}
var fromList = [];
var cols = [];

// var dbCols = ['','trade_date','code','close','name'];
var dbCols = [];
var wfCols = ['','AVG','MAX','MIN'];
let operators= ['','+','-','=','lt','gt','lte', 'gte'];

$(document).ready(function () {

    $("input[name=name]").on('blur', function (e) {
        var name = $(this).val();
        console.log(name);
        cte["name"] = name;
    });

    $("button#from-add").click(function (e) {
        e.preventDefault();
        var selectedFrom = $("select[name=from]").find(":selected")
        var option = selectedFrom.val();
        var text = selectedFrom.text();

        // If CTE then associate parent
        if(text.includes('cte')){
            cte['parent'] = option;
        }else{
            cte['parent'] = '';
        }

        console.log(option);

        $("span#from-list").append("<em>" + option + "</em>");
        fromList.push(option);
        cte['from'] = fromList;

        // Populate dbCols
        $.ajax({
                type: "GET", 
                dataType:"json",
                url: '/fetchtablemeta/'+option, //localhost Flask
                data : {},
                contentType: "application/json",
            }).done(function(data){
              
                dbCols = data['res']
                $("div#where-list").append(addWhereCondition());
                $("div#order-list").append(addOrderCondition());
            });



          

    });

    $("button#col-add").click(function (e) {
        e.preventDefault();
        var option = $("select[name=column]").val();
        if (option === 'normal') {
            var column = addNormalColumn();
            $("div#col-list").append(column);
        } else if (option === 'window') {
            var column = addWindowColumn();
            $("div#col-list").append(column);
        } else if (option === 'case') {
            var column = addCaseColumn();
            var thenColumn = addThenColumn();
            var elseColumn =addElseColumn();
            $("div#col-list").append("<div class='case-column'><label>Alias Name</label><input type='text' name='case-alias'/>" + column + "<div> then"+thenColumn +  "else " + elseColumn + "</div></div>");
        }


       
    });

  

    $('div#col-list').on('change', 'select[name=select-normal-col]', function (event) {
        var name = $(this).val();
        var selectedValue = this.selectedOptions[0].value;
        var selectedText = this.selectedOptions[0].text;
        console.log(name, selectedValue);
        // cols.push({ "name": name, "type": "normal" });
    });


    $("form#sqlform").submit(function (e) {
        var action = $(e.originalEvent.submitter).val();
        cols = []
        e.preventDefault();      
        // parse all Normal Column
        let normalCols = [];
        $(this).find("div.normal-column").each((i,e)=>{
            console.log(i,e);
            let val = $(e).find(":selected").val();
            cols.push({
                "name":val,
                "type":"normal"

            });
        });
        

        // parse all Window Column
        var winCols = [];
        $(this).find("div.window-column").each((i,e)=>{
            console.log(i,e);
            let parent = $(e);
            let wf = $(parent).find("select[name=select-wf-wf]").val();
            let col = $(parent).find("select[name=select-window-col]").val();
            let partitionByColumn = $(parent).find("select[name=select-partition-by-col]").val();
            let orderByColumn = $(parent).find("select[name=select-order-by-col]").val();
            let orderByType = $(parent).find("select[name=select-order-type]").val();
    
            let preceding = $(parent).find("select[name=select-preceding-col]").find(":selected").text();
            let following = $(parent).find("select[name=select-following-col]").find(":selected").text();
            // let precedingRowNum = $(parent).find("select[name=select-preceding-col]").find(":selected").val();
            // let followingRowNum = $(parent).find("select[name=select-following-col]").find(":selected").val();
            let alias = $(parent).find("input[name=window-func-alias]").val();
    
            cols.push({
                "name": alias,
                "type": "window_function",
                "attributes": {
                    "window_func": wf,
                    "col": col,
                    "over": {
                        "partition_by": partitionByColumn,
                        "order_by": orderByColumn,
                        "order_type": orderByType,
                        "frame_spec": {
                            "type": "rows"
                        },
                        "frame_boundaries": {
                            "preceding": preceding,
                            "following": following
                        }
                    }
                }
            });
            console.log(cols);
        });

        // parse all Case Column
        var caseCols = [];
        $(this).find("div.case-column").each((i,e)=>{
            // console.log(i,e);
            let alias = $(e).find("input[name=case-alias]").val();
            console.log(alias);
            let when = [];
            let then = '';
            let elsecond = '';
            $(e).find("select").each(function(i,e){
            // console.log(i,e);
            console.log($(e).attr("name"));
                if ($(e).attr("name") === "select-case-then-col"){
                    then =  $(e).find(":selected").text();
                    // console.log("then",then)
                }else if ($(e).attr("name") === "select-case-else-col"){
                    elsecond =  $(e).find(":selected").text();
                
                }else{
                    let val = $(e).find(":selected").val();
                    let text = $(e).find(":selected").text();
                    when.push(text);
                    // console.log("when",when)
                    // if(val === 'value'){
                    //     console.log(val,text);
    
                    // }else{
                    //     console.log(val,text);
                    // }

                }
             
              
                
            });
            console.log("when then",when,then);
            cols.push({
                "name":alias,
                "type":"case",              
                "attributes":{
                    "when":when,
                    "then":then,
                    "else":elsecond
                }
            });
            console.log(caseColumns);
            
        });

       
       
        // where
        var where = [];
        $(this).find("div#where-list > select").each((i,e)=>{
            let text = $(e).find(":selected").text();
            if(text !== ""){
                console.log(text);
                where.push(text);
            }
          
        });
        
        // where
        var order = [];
        $(this).find("div#order-list > select").each((i,e)=>{
            let text = $(e).find(":selected").text();
            if(text !== ""){
                console.log(text);
                order.push(text);
            }
        });
            


        // cols.push(normalCols);
        // cols.push(winCols);
        // cols.push(caseCols);

        var limit = $("input[name=limit]").val();
        var offset = $("input[name=offset]").val();

       
        cte['cols'] = cols;
        cte['where'] = where;
        cte['order'] = order;
        cte['limit'] = limit;
        cte['offset'] = offset;

        console.log(cte);

        $.ajax({
            type: "POST", 
            dataType:"json",
            url: "/jsontosql/" + action, //localhost Flask
            data : JSON.stringify([cte]),
            contentType: "application/json",
        }).done(function(data){
            console.log(data);
            console.log(data['sql']);
            $("pre#generated-sql").html(data['sql']);
            $("pre#res").html(data['res']);
            console.log(data['res'][0]);
            var res = JSON.parse(data['res']);
            var keys = Object.keys(res[0]);

            // Create table
            var table = `<table class="table"><thead><tr>`;
            for(var k in keys){
                table += `<th>${keys[k]}</th>`;
            }
            table += `</tr>`;
            table += `</thead><tbody>`;
            for(var r in res){
                table += `<tr>`;
                for(var k in keys){
                    table += `<td>${res[r][keys[k]]}</td>`;
                }
                table += `</tr>`;
            }
            table += `</tbody></table>`;
            $("pre#res").html(table);
        });
    });// End of submit

  
}); // End of Document ready


function addNormalColumn() {

    var cols = dbCols;

    var columns = `<select name="select-normal-col">`;
    for (var col in cols) {
        columns += `<option value = ${cols[col]}>${cols[col]}</option>`;
    }
    columns += `</select>`;
    var normalColumn = `<div class="normal-column"><label>Select Column</label>${columns}</div>`;
    return normalColumn;

}
function addWindowColumn() {
    var windowFunc = wfCols;
    var cols = dbCols;

    var wf = `<select name="select-wf-wf">`;
    for (var w in windowFunc) {
        wf += `<option value = ${windowFunc[w]}>${windowFunc[w]}</option>`;
    }
    wf += `</select>`;


    var columns = `<select name="select-window-col">`;
    for (var col in cols) {
        columns += `<option value = ${cols[col]}>${cols[col]}</option>`;
    }
    columns += `</select>`;

    var partitionByColumn = `<select name="select-partition-by-col">`;
    for (var col in cols) {
        partitionByColumn += `<option value = ${cols[col]}>${cols[col]}</option>`;
    }
    partitionByColumn += `</select>`;

    var orderByColumn = `<select name="select-order-by-col">`;
    for (var col in cols) {
        orderByColumn += `<option value = ${cols[col]}>${cols[col]}</option>`;
    }
    orderByColumn += `</select>
    <select name="select-order-type">
        <option value=""></option>
        <option value="asc">asc</option>
        <option value="desc">desc</option>
    </select>`;


    var preceding = `<select name="select-preceding-col" onchange="onChangePreceding(this)">

        <option value =""></option>
        <option value ="preceding">preceding</option>
        <option value ="current row">current Row</option>

    </select>`;

    var following = `<select name="select-following-col" onchange="onChangeFollowing(this)">
        <option value =""></option>
        <option value ="following" >following</option>
        <option value ="current row">current Row</option>
    </select>`;

    var normalColumn = `<div class="window-column">${wf} <bold>(</bold> ${columns}<bold>)</bold> OVER ( PARTITION BY ${partitionByColumn} ORDER BY ${orderByColumn} ROWS BETWEEN ${preceding} AND ${following} <label>ALIAS</label> <input type="text" name="window-func-alias" /><br/></div>`;
    return normalColumn;

}

function addCaseColumn() {
    var cols = dbCols;
    
    var lcolumns = `<div><select name="select-case-lval-col" onchange="onChangeCaseColumns(this)">`;


    for (var col in cols) {
        lcolumns += `<option value ='column'}>${cols[col]}</option>`;
                   
    }
    lcolumns +=  `<option value="value">value</option>`;
    lcolumns += `</select>`;

    var rcolumns = `<select name="select-case-rval-col" onchange="onChangeCaseColumns(this)">`;
    for (var col in cols) {
        rcolumns += `<option value = ${cols[col]}>${cols[col]}</option>`;
                   
    }
    rcolumns +=  `<option value="value">value</option>`;
    rcolumns += `</select>`;

    var operator = `<select name="select-case-operator-col">`;
    for (var op in operators) {
        operator += `<option value = operator>${operators[op]}</option>`;
    }
    operator += `</select>`;



    var andor = `<select name="select-case-andor-col" onchange="onChangeCaseAndOr(this)">
                    <option></option>
                    <option value="and">and</option>
                    <option value="or">or</option>
                 </select>
    `;

    var normalColumn = `${lcolumns} ${operator} ${rcolumns} ${andor}</div>`;

   
    
    // normalColumn += `<br/>`;
    return normalColumn;

}

function addThenColumn(){
    var cols = dbCols;
    var rcolumns = `<select name="select-case-then-col" onchange="onChangeCaseColumns(this)">`;
    for (var col in cols) {
        rcolumns += `<option value = ${cols[col]}>${cols[col]}</option>`;
                   
    }
    rcolumns +=  `<option value="value">value</option>`;
    rcolumns += `</select>`;
    return rcolumns;
}

function addElseColumn(){
    var cols = dbCols;
    var rcolumns = `<select name="select-case-else-col" onchange="onChangeCaseColumns(this)">`;
    for (var col in cols) {
        rcolumns += `<option value = ${cols[col]}>${cols[col]}</option>`;
                   
    }
    rcolumns +=  `<option value="value">value</option>`;
    rcolumns += `</select>`;
    return rcolumns;
}

function convertFormToJSON(form) {
    const array = $(form).serializeArray(); // Encodes the set of form elements as an array of names and values.
    const json = {};
    $.each(array, function () {
        json[this.name] = this.value || "";
    });
    return json;
}

function onChangePreceding(e) {

    // var selectedValue = this.selectedOptions[0].value;
    // var selectedText  = this.selectedOptions[0].text;
    if ($(e).find(":selected").val() == 'preceding') {
        let precedingRowNum = prompt("Please enter preceding row", "");
        var fullText = precedingRowNum + " preceding";
        $(e).find(":selected").text(fullText);
        $(e).find(":selected").val(precedingRowNum);
    }

}
function onChangeFollowing(e) {
    // var selectedValue = this.selectedOptions[0].value;
    // var selectedText  = this.selectedOptions[0].text;
    if ($(e).find(":selected").val() == 'following') {
        let followingRowNum = prompt("Please enter following row", "");
        var fullText = followingRowNum + " following";
        $(e).find(":selected").text(fullText)
        $(e).find(":selected").val(followingRowNum)
    }

}

var caseColumns = [];
function onChangeCaseColumns(e){   
    if ($(e).find(":selected").val() == 'value') {
        let value = prompt("Please enter value", "");
        // var fullText = value + " following";
        $(e).find(":selected").text(value)
        // $(e).find(":selected").val('value')


    }


}

function onChangeCaseAndOr(e){
    let ao = $(e).find(":selected").val();
    if (ao == 'and' || ao == 'or') {
       $(e).parent().parent().append(addCaseColumn());
    }
}
function onChangeWhereAndOr(e){
    let ao = $(e).find(":selected").val();
    if (ao == 'and' || ao == 'or') {
       $(e).parent().append(addWhereCondition());
    }
}

// where condition
function addWhereCondition() {
    var cols = dbCols;
    var lcolumns = `<select name="select-case-lval-col" onchange="onChangeCaseColumns(this)">`;


    for (var col in cols) {
        lcolumns += `<option value ='column'}>${cols[col]}</option>`;
                   
    }
    lcolumns +=  `<option value="value">value</option>`;
    lcolumns += `</select>`;

    var rcolumns = `<select name="select-case-rval-col" onchange="onChangeCaseColumns(this)">`;
    for (var col in cols) {
        rcolumns += `<option value = ${cols[col]}>${cols[col]}</option>`;
                   
    }
    rcolumns +=  `<option value="value">value</option>`;
    rcolumns += `</select>`;

    var operator = `<select name="select-case-operator-col">`;
    for (var op in operators) {
        operator += `<option value = operator>${operators[op]}</option>`;
    }
    operator += `</select>`;



    var andor = `<select name="select-case-andor-col" onchange="onChangeWhereAndOr(this)">
                    <option></option>
                    <option value="and">and</option>
                    <option value="or">or</option>
                 </select>
    `;

    var normalColumn = `${lcolumns} ${operator} ${rcolumns} ${andor}`;

   
    
    // normalColumn += `<br/>`;
    return normalColumn;

}


function addOrderCondition() {
    var cols = dbCols;


    var orderByColumn = `<select name="select-order-by-type">`;
    for (var col in cols) {
        orderByColumn += `<option value = ${cols[col]}>${cols[col]}</option>`;
    }
    orderByColumn += `</select>`;
    var orderByType = `<select name="select-order-type" onchange="onChangeOrderBy(this)">
        <option value=""></option>
        <option value="asc">asc</option>
        <option value="desc">desc</option>
    </select>`;
    var normalColumn = `${orderByColumn} ${orderByType}`;
    return normalColumn;

}

function onChangeOrderBy(e){
    $(e).parent().append(addOrderCondition());
}

