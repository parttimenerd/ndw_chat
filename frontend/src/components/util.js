import {SERVER_LOCATION} from "../config";

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

export function get_tracks(callback) {
        own_fetch("tracks", {}, res => callback(res["tracks"]))
}