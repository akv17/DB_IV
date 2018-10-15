function clearFormsBlock(){
    let formsBlock = document.querySelector(".forms_block");
    formsBlock.style.display = "none";

    for (let child of Array.from(formsBlock.children)){
        child.style.display = "none";
    }
}

function clearSubMenu(){
    let subMenu = document.querySelector(".sub_menu");
    subMenu.style.display = "none";
    
    document.querySelector("#fetch_all").children[0].name = "";

    for (let child of Array.from(subMenu.children)){
        child.style.background = "";
        child.style.color = "";
    }
}


function addSubMenu(){
    document.querySelector(".sub_menu").style.display = "";
    document.querySelector("#fetch_all").children[0].name = `${activeMenuId}_fetch_all`;
}

function activateMenu(id, clearOutput=true){
    if (id == "none"){
        return;            
    }

    let block = document.querySelector(".menu");
    let menu = block.querySelector(`#${id}`);
    activeMenuId = menu.id;

    // clearing up
    if (clearOutput) {document.querySelector("#report_message").innerHTML = "";}
    clearFormsBlock();             
    clearSubMenu();


    for (let button of Array.from(block.children)){
        if (button.id == id){
            button.style.background = "#3385ff";
            button.style.color = "white";
        }

        else {
            button.style.background = "";
            button.style.color = "";
        }
    }

    // adding sub blocks onto current menu
    addSubMenu();
}


function addOutputWindow(x){
    outputWindow.style.display = "";
}        

function addFormsBlock(){
    let formsBlock = document.querySelector(".forms_block");
    formsBlock.style.display = "";

    for (let child of Array.from(formsBlock.children)){
        if (child.id == `${activeMenuId}_${activeSubMenuId}_form`){
            child.style.display = "";
            child.children[0].name = `${activeMenuId}_${activeSubMenuId}`;
        }
    }
}

function activateSubMenu(id, clearOutput=true){
    if (id == "none"){
        return;
    }

    let block = document.querySelector(".sub_menu");
    let subMenu = block.querySelector(`#${id}`);
    activeSubMenuId = subMenu.id;

    // clearing up
    if (clearOutput) {document.querySelector("#report_message").innerHTML = "";}
    clearFormsBlock();             

    for (let button of Array.from(block.children)){
        if (button.id == id){
            button.style.background = "#3385ff";
            button.style.color = "white";
        }

        else {
            button.style.background = "";
            button.style.color = "";
        }
    }

    // adding sub blocks
    addFormsBlock();
}

function applyCommit(event){
    alert("Confirm committing");
}

activateMenu(activeMenuId, false);
activateSubMenu(activeSubMenuId, false);

document.querySelector(".commit_form").addEventListener("submit", applyCommit);

for (let button of document.getElementsByClassName("menu_button")){
    button.addEventListener("click", event => {activateMenu(event.target.id);})
}

for (let button of document.getElementsByClassName("sub_menu_button")){
    button.addEventListener("click", event => {activateSubMenu(event.target.id);})
}