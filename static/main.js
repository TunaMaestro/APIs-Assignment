window.onload = function () {
    let submitter = document.getElementById('filter-submit')
    submitter.addEventListener('click', function (e) {
            e.preventDefault();
            // console.log(active.toString());
            const activeStr = activeToStr(active);
            const query = activeStr + $('#filter').serialize() + "&df=true"
            $.post("test", query, function(response) {
                document.getElementById('df').innerText = response
            });



            // Plotly.plot('main-graph', response, {});
        }
    )


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
            e.preventDefault();
            let id = e.target.getAttribute('id');
            // console.log(active[id]);
            active[id][0] = !active[id][0];

            // alert("set " + id + " to " + activeClasses[+ active[id][0]]);
            active[id][1].setAttribute('class', activeClasses[+active[id][0]]); // turns the bool into a number
        })
    }
};

function activeToStr(active) {
    let s = "";
    for (let i in active) {
        s += i + "=" + active[i][0].toString() + "&";
    }
    return s;
}