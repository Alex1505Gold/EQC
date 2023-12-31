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

const video = document.getElementById('video-element')
const image = document.getElementById('img-element')
const captureBtn = document.getElementById('cpt-btn')
const reloadBtn = document.getElementById('rld-btn')

reloadBtn.addEventListener('click', () => {
    window.location.reload()
})

if (navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({video: true})
    .then((stream) => {
        video.srcObject = stream
        const {height, width} = stream.getTracks()[0].getSettings()

        captureBtn.addEventListener('click', e=> {
            e.preventDefault()
            captureBtn.classList.add('not-visible')
            const track = stream.getVideoTracks()[0]
            const imageCapture = new ImageCapture(track)
            console.log(imageCapture)

            imageCapture.takePhoto().then(blob => {
                console.log("took photo:", blob)
                const img = new Image(width, height)
                img.src = URL.createObjectURL(blob)
                image.append(img)

                video.classList.add('not-visible')

                const reader = new FileReader()

                reader.readAsDataURL(blob)
                reader.onloadend = () => {
                    const base64data = reader.result

                    const fd = new FormData()
                    fd.append('csrfmiddlewaretoken', csrftoken)
                    fd.append('photo', base64data)

                    $.ajax({
                        type: 'POST',
                        url: '/classify/',
                        enctype: 'multipart/form-data',
                        data: fd,
                        processData: false,
                        contentType: false,
                        success: (resp) => {
                            console.log(resp)
                            const str_resp = JSON.stringify(resp)
                            if (str_resp.indexOf('true') > -1){
                                window.location.href = '/student/'
                            }
                            else {
                                alert(`Your face wasn't recognised\nPlaese try again or contact the administator`)
                            }
                        },
                        error: (err) => {
                            console.log(err)
                        }
                    })
                }
            }).catch(error => {
                console.log('takePhoto() error: ', error);
            });
        });
    })
    .catch(error => {
        console.log("Something went wrong!", error);
    });
}