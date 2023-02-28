
function flattenObj(obj, parent = '', res = {}){
    for(let key in obj){
        let propName = parent ? parent + '.' + key : key;
        if(typeof obj[key] == 'object'){
            flattenObj(obj[key], propName, res);
        } else {
            res[propName] = obj[key];
        }
    }
    return res;
}




let tableFromJson = (data) => {

    let leaves = data;
    //let leaves = flattenObj(data);
    // Extract value from table header. 
    // ('Book ID', 'Book Name', 'Category' and 'Price')

    const table = document.createElement("table");

    for (let key in leaves) {
        
        let tr = table.insertRow(-1); 
        let tabCell = tr.insertCell(-1);
        tabCell.innerHTML = key;
    
        for (let prop in leaves[key])
        {
            let cell = tr.insertCell(-1);
            cell.innerHTML = leaves[key][prop];
        }
    }

    // Create table.
    

    // Create table header row using the extracted headers above.
    /*let tr = table.insertRow(-1);   
    table.insert                // table row.

    for (let i = 0; i < col.length; i++) {
      let th = document.createElement("th");      // table header.
      th.innerHTML = col[i];
      tr.appendChild(th);
    }

    // add json data to the table as rows.
    for (let i = 0; i < leaves.length; i++) {

      tr = table.insertRow(-1);

      for (let j = 0; j < col.length; j++) {
        let tabCell = tr.insertCell(-1);
        tabCell.innerHTML = leaves[i][col[j]];
      }
    }*/

    return table;
  }

