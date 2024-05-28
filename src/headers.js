// /etc/nginx/headers.js
function escapeJsonString(str) {
    return str.replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/\n/g, '\\n').replace(/\r/g, '\\r');
}

function headers_json(r) {
    var headers = {};
    for (var h in r.headersIn) {
        headers[h] = escapeJsonString(r.headersIn[h]);
    }
    return JSON.stringify(headers);
}

export default {headers_json};
