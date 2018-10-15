function assignId(event){
    let atrMap = {'projects': 'FreelancerId', 'freelancers': 'ProjectId'};
    let recordId = event.target.children[1].value;
    let assignedId = prompt("Assign id:");

    if (!assignedId){
        event.preventDefault();
        return;
    }

    event.target.children[2].value = assignedId;

    let atr = atrMap[activeMenuId];
    let recordInOutput = document.querySelector(`#${activeMenuId}_${recordId}_${atr}`);
    
    recordInOutput.innerHTML = `<span style="font-style: italic;">${atr}</span>: ${assignedId}`;
}

function cancelId(event){
    alert("Confirm cancelling");
    let atrMap = {'projects': 'FreelancerId', 'freelancers': 'ProjectId'};
    let recordId = event.target.children[1].value; 

    let atr = atrMap[activeMenuId];
    let recordInOutput = document.querySelector(`#${activeMenuId}_${recordId}_${atr}`);

    let prevAssignedId = recordInOutput.textContent.split(': ')[1];
    event.target.children[2].value = prevAssignedId;

    recordInOutput.innerHTML = `<span style="font-style: italic;">${atr}</span>: -1`;
}

function removeRecord(event){
    alert("Confirm removal");
    relistOutputWindow(event.target.parentNode.id);
}

function relistOutputWindow(nodeToRemoveId){
    let olElement = Array.from(outputWindow.children)[1];
    let liElements = Array.from(olElement.children);
    let nodeToRemove;

    olElement.innerHTML = "";

    for (let node of liElements){
        if (node.id != nodeToRemoveId){
            olElement.appendChild(node);
        }
        else {
            nodeToRemove = node;
            console.log(nodeToRemove)
        }
    }
    nodeToRemove.style.display = "none";
    olElement.appendChild(nodeToRemove);
}

for (let node of document.getElementsByClassName("assign_form")){
    node.addEventListener("submit", assignId);
}

for (let node of document.getElementsByClassName("cancel_form")){
    node.addEventListener("submit", cancelId);
}

for (let node of document.getElementsByClassName("remove_form")){
    node.addEventListener("submit", removeRecord);
}