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

        function red(toWhere) {
            window.location.replace(`${toWhere}`)
        }
