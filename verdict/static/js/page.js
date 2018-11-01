

function replace_param(url, param, replace_with) {
    var re = eval('/('+ param+'=)([^&]*)/gi');
    if(url.indexOf(param + '=') > 0){
        var nurl = url.replace(re, param+ '=' + replace_with);
    }else{
        if(url.indexOf('?') > 0) {
            var nurl = url + '&' + param + '=' + replace_with;
        }else{
            var nurl = url + '?' + param + '=' + replace_with;
        }
    }
    return nurl;
}


function next_page(page, total_pages) {
    var npage = page + 1;
    if(npage > total_pages){
        // alert('It\'s the last page');
        return;
    }
    var url = window.location.href;
    var nurl = replace_param(url, 'page', npage);
    location.href = nurl;
}


function previous_page(page) {
    var ppage = page - 1;
    if(ppage < 1){
        // alert('It\'s the first page');
        return;
    }
    var url = window.location.href;
    var nurl = replace_param(url, 'page', ppage);
    location.href = nurl;
}


function search() {
    var name = $("#search").val();
    var url = window.location.href;
    var real_url = url.split('?')[0];
    location.href = real_url + '?name=' + name;
}