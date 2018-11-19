function handle(event) {
    let form = event.target;

    if (form.className == 'del_form') {
        alert('Confirm deletion');
    }
    
    let form = event.target;
    
    let _id = form.parentNode.parentNode.id;
    
    form.children[1].value = _id;
}


for (let button of document.querySelectorAll('form')) {
    button.addEventListener('submit', handle);
}
