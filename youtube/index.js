import {api_key, server, video_per_track} from "./config.js";

import request from "request";

import YouTube from "./youtube.js";

function push(track, content) {
    request.post({
        headers: {'content-type': 'application/json'},
        url: server,
        body: JSON.stringify({
            track: track,
            content: content
        })
    }, function (error, response, body) {
        // console.log(body);
    });
}

const startTime = Date.now().valueOf();

for (let track in video_per_track) {
    const yt = new YouTube(video_per_track[track], api_key);
    yt.on('ready', () => {
        console.log('ready!')
        yt.listen(1000)
    })
    yt.on('message', data => {
        const message = data.snippet.displayMessage;
        const publishedAt = Date.parse(data.snippet.publishedAt).valueOf();
        if (publishedAt >= startTime) {
            console.info(`Got messages '${message}' in track ${track}`)
            push(track, message);
        }
    })

    yt.on('error', error => {
        console.error(error)
    })

}

