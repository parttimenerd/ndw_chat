// copied from https://github.com/Sudobeast/youtube-live-chat/blob/patch-1/index.js
// and slightly modified

import request from 'request';
import {EventEmitter} from 'events'

/**
 * The main hub for acquire live chat with the YouTube Date API.
 * @extends {EventEmitter}
 */
class YouTube extends EventEmitter {
  /**
   * @param {string} video id
   * @param {string} APIKey You'r API key
   */
  constructor(videoId, apiKey) {
    super()
    this.videoId = videoId
    this.key = apiKey
    this.getChatId()
  }

  getChatId() {
    const url = 'https://www.googleapis.com/youtube/v3/videos'+
      '?part=liveStreamingDetails&key=' + this.key +
      `&id=${this.videoId}`+
      `&part=snippet,liveStreamingDetails`
    this.request(url, data => {
      if (!data.items.length)
        this.emit('error', 'Can not find chat.')
      else {
        this.chatId = data.items[0].liveStreamingDetails.activeLiveChatId
        this.emit('ready')
      }
    })
  }

  /**
   * Gets live chat messages.
   * See {@link https://developers.google.com/youtube/v3/live/docs/liveChatMessages/list#response|docs}
   * @return {object}
   */
  getChat() {
    if (!this.chatId) return this.emit('error', 'Chat id is invalid.')
    const url = 'https://www.googleapis.com/youtube/v3/liveChat/messages'+
      `?liveChatId=${this.chatId}`+
      '&part=id,snippet,authorDetails'+
      '&maxResults=2000'+
      `&key=${this.key}`
    this.request(url, data => {
      this.emit('json', data)
    })
  }

  request(url, callback) {
    request({
      url: url,
      method: 'GET',
      json: true,
    }, (error, response, data) => {
      if (error)
        this.emit('error', error)
      else if (response.statusCode !== 200)
        this.emit('error', data)
      else
        callback(data)
    })
  }

  /**
   * Gets live chat messages at regular intervals.
   * @param {number} delay Interval to get live chat messages
   * @fires YouTube#message
   */
  listen(delay) {
    let lastRead = 0, time = 0
    this.interval = setInterval(() => this.getChat(), delay)
    this.on('json', data => {
      for (const item of data.items) {
        time = new Date(item.snippet.publishedAt).getTime()
        if (lastRead < time) {
          lastRead = time
          /**
          * Emitted whenever a new message is recepted.
          * See {@link https://developers.google.com/youtube/v3/live/docs/liveChatMessages#resource|docs}
          * @event YouTube#message
          * @type {object}
          */
          this.emit('message', item)
        }
      }
    })
  }

  /**
   * Stops getting live chat messages at regular intervals.
   */
  stop() {
    clearInterval(this.interval)
  }
}

export default YouTube
