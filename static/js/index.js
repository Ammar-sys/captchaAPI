        function mouseOver(btn) {
            let element = document.getElementById(`${btn}`)
            element.style.color = "#87898a";
            element.style.background = "#1b1e1f";
        }

        function mouseOut(btn) {
		    let element = document.getElementById(`${btn}`)
            element.style.color = "#fff";
            element.style.background = "#212529";
        }

        function examples() {
            window.location.replace('/docs')
        }

        function supportserver() {
            window.location.replace('https://discord.gg/gngRDu5q')
        }

        function gt() {
            window.location.replace('https://github.com/ammarsys/captchaAPI')
        }

        function ex() {
            window.location.replace('/examples')
        }

        function me() {
            window.location.replace('/api/img')
        }
