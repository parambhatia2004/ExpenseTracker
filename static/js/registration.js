function checkInput(email, password, repassword){
    if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) == false){
        alert("Enter a valid email");
        return false;
    }
}
