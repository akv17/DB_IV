function styleButtonActivation(className) {
    const button = document.querySelector(`.${className}`)
    button.style.background = '#3385ff';
    button.style.color = 'white'; 
}

function styleButtonDeactivation(className) {
    const button = document.querySelector(`.${className}`)
    
    button.style.background = '';
    button.style.color = ''; 
}

function activateSqlTableSelector() {
    document.querySelector('.sql_table_selector').style.display = '';   
}

function deactivateSqlTableSelector() {
    document.querySelector('.sql_table_selector').style.display = 'none';   
}

function getSelectedSqlTable () {
    const selectedIndex = document.querySelector('#dropdown').selectedIndex;
    return dropdownIndexToTablePrefix[selectedIndex];
}

function activateOpForm(opButtonClass) {   
    // cleaning up
    deactivateOpForm();
    clearStatusLog();
    
    activeOpFormClass = `${getSelectedSqlTable()}_${opButtonClass}`;

    document.querySelector(`.${activeOpFormClass}`).style.display = '';
    console.log(`activated`);
}

function deactivateOpForm() {
    if (activeOpFormClass === 'none') {
        return;
    }

    document.querySelector(`.${activeOpFormClass}`).style.display = 'none';
}

function activateOpMenu(event, className=undefined) {
    // cleaning up
    deactivateOpMenu();
    clearStatusLog();

    // deactivating if active menu clicked
    if (event && activeOpButtonClass == event.target.className) {
        activeOpButtonClass = 'none';
        return;
    }
    
    activeOpButtonClass = event ? event.target.className : className;

    styleButtonActivation(activeOpButtonClass);

    activateSqlTableSelector();

    activateOpForm(activeOpButtonClass);
}

function deactivateOpMenu() {
    if (activeOpButtonClass === 'none') {
        return;
    }
    
    deactivateOpForm();

    deactivateSqlTableSelector();

    styleButtonDeactivation(activeOpButtonClass);
}

function handleDropdownSelectedChange(event) {
    deactivateOpForm();

    activateOpForm(activeOpButtonClass);
}

function activateColsSelector(event) {
    const selector = document.querySelector(`#${getSelectedSqlTable()}_${activeOpButtonClass}_cols_selector`);

    if (selector.style.display == 'none') {
        selector.style.display = '';
        styleButtonActivation(event.target.className);
    }

    else {
        selector.style.display = 'none';
        styleButtonDeactivation(event.target.className);
    }
}

function clearStatusLog() {
    document.querySelector('.status_log').textContent = '';
}

const dropdownIndexToTablePrefix = {0: 'msg', 1: 'usr'};

let activeOpButtonClass = 'none';
let activeOpFormClass = 'none';

if (activeOpButtonClass !== 'none') {
    activateOpMenu(undefined, className=activeOpButtonClass);
}

for (const button of document.querySelectorAll('.op_menu')) {
    button.addEventListener('click', activateOpMenu);
}

document.querySelector('#dropdown').addEventListener('change', handleDropdownSelectedChange)

for (const trigger of document.querySelectorAll('.cols_selector_trigger')) {
    trigger.addEventListener('click', activateColsSelector);
}