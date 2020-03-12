window.onload = () => {
    const inputs = document.querySelectorAll("input[type=number]");

    for ( let i=0; i<inputs.length; i++ ) {
        inputs[i].addEventListener('change', updateInputValue, false);
    }
}

function updateInputValue(e) {
    if ( Number.isInteger(Number( e.target.value ) ) ) {
        e.target.value  = parseInt( e.target.value, 10  );
    } else {
        e.target.value  = parseFloat( e.target.value ).toFixed(2);
    }
}
