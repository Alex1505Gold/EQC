const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

const userField = document.getElementById('user-element')
const passwordField = document.getElementById('password-element')
const captureBtn = document.getElementById('cpt-btn')

captureBtn.addEventListener('click', e=> {
    e.preventDefault()
    const fd = new FormData()
    fd.append('csrfmiddlewaretoken', csrftoken)
    fd.append('user', userField.value)
    fd.append('password', passwordField.value)
    $.ajax({
        type: 'POST',
        url: '/password_auth/',
        enctype: 'multipart/form-data',
        data: fd,
        processData: false,
        contentType: false,
        success: (resp) => {
            console.log(resp)
            const str_resp = JSON.stringify(resp)
            const obj_resp = JSON.parse(str_resp)
            if (obj_resp.success == true){
                window.location.href = '/prof/'
            }
            else {
                alert(obj_resp.info)
            }
        },
        error: (err) => {
            console.log(err)
        }
    })
})