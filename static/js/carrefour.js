clicado = false
document.body.addEventListener('click', (event) => {
    if (!clicado) {
        const audio = document.createElement('audio');
        console.log('audio');
        audio.src = "/static/mp3/carrefour.mp3";
        audio.loop = true;
        audio.volume = 1;
        audio.play();
        document.body.appendChild(audio);

        const audio2 = document.createElement('audio');
        console.log('audio2');
        audio2.src = "/static/mp3/mercadona.mp3";
        audio2.loop = true;
        audio2.volume = 1;
        audio2.play();
        document.body.appendChild(audio2);

        const audio3 = document.createElement('audio');
        console.log('audio3');
        audio3.src = "/static/mp3/bara.mp3";
        audio3.loop = true;
        audio3.volume = 1;
        audio3.play();
        document.body.appendChild(audio3);
        clicado = true;
    }
});
 