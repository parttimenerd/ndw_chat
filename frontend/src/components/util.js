import {SERVER_LOCATION} from "../config";
import Cookies from "js-cookie"

export function own_fetch(subpage, args, callback) {
    fetch(`${SERVER_LOCATION}/${subpage}?${new URLSearchParams(args)}`, {
        method: "GET",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    }).then(res => res.json())
        .then(data => callback(data))
}

export function send_message(track, content) {
    fetch(`${SERVER_LOCATION}/send`, {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
                "track": track,
                "content": content
            })
    });
}

export function get_tracks(callback) {
        own_fetch("tracks", {}, res => callback(res["tracks"]))
}

/** callback(is password correct) */
export function check_password(password, callback) {
        own_fetch("check_password", {"password": password}, res => callback(res["matches"]))
}

export function password_from_cookie() {
    return Cookies.get("password");
}