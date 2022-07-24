window.onload = function () {
    let submitter = document.getElementById('filter-submit')
    submitter.addEventListener('click', function (e) {
        e.preventDefault()
        update_plot();
    })


    const filterSettings = document.getElementsByClassName("filter-setting");
    const activeClasses = ["filter-setting nav-link text-white", "filter-setting nav-link text-white active"];
    // console.log(filterSettings);

    let active = {}
    for (let i = 0; i < filterSettings.length; i++) {
        let e = filterSettings[i];
        active[e.getAttribute('id')] = [false, e];
    }

    active['filter-all'][0] = true;


    // console.log(active)
    for (let i = 0; i < filterSettings.length; i++) {
        filterSettings[i].addEventListener('click', function (e) {
            mode_clicked(e);
            update_plot(e);
        })
    }

    document.getElementById("filter").addEventListener("input", function () {
        update_plot()
    })


    function mode_clicked(e) {

        e.preventDefault();
        let id = e.target.getAttribute('id');


        // console.log(active[id]);
        active[id][0] = !active[id][0];
        // console.log(id, active[id][0])
        if (id === "filter-all") {
            if (active[id][0]) {
                for (let i in active) {
                    if (i === "filter-all") {
                        continue
                    }
                    active[i][0] = false;
                    active[i][1].setAttribute('class', activeClasses[0]);
                }
            }
        } else {
            active["filter-all"][0] = false;
            active["filter-all"][1].setAttribute('class', activeClasses[0]);
        }
        // test if all transport modes are selected
        let allTrue = true
        for (let i in active) {
            if (i === "filter-all") {
                continue
            }
            allTrue = allTrue && active[i][0]
            // console.log(i + " : " + allTrue)
        }
        if (allTrue) {
            active[id][1].setAttribute('class', activeClasses[1])
            setTimeout(function () {
                for (let i in active) {
                    active[i][0] = false;
                    active[i][1].setAttribute('class', activeClasses[0]);
                }
                active["filter-all"][0] = true;
                active["filter-all"][1].setAttribute('class', activeClasses[1]);

            }, 100)
        }

        // alert("set " + id + " to " + activeClasses[+ active[id][0]]);
        active[id][1].setAttribute('class', activeClasses[+active[id][0]]); // turns the bool into a number
    }

    function update_plot() {
        // console.log(active.toString());
        const activeStr = activeToStr(active);
        const query = activeStr + $('#filter').serialize() + "&df=true"
        $.post("update_graphs", query, function (response) {
                // document.getElementById('df').innerText = response
            response = JSON.parse(response)
                Plotly.react('main-graph', response[0], {});
                Plotly.react('box-plots-graph', response[1], {});
            }
        )
    }
};


function activeToStr(active) {
    let s = "";
    for (let i in active) {
        s += i + "=" + active[i][0].toString() + "&";
    }
    return s;
}