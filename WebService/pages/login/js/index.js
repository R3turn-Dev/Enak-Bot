function twitch() {
    window.open(twitch_uri, "_blank", "height=650, width=800");
}

function discord() {
    window.open(discord_uri, "_blank", "height=650, width=800");
}

function success() {
    let rurl = new URL(location.href).searchParams.get("redirect");
    if(rurl) {
        location.href = rurl;
    } else {
        location.href = "/";
    }
}
