import {writable,} from 'svelte/store';

export let hostMessageStore = writable("");
export let messageStore = writable([]);

export class WebSocketHandler {
    constructor(server, password, track, showRaw, notificationContext) {
        this.server = server;
        this.password = password;
        this.track = track;
        this.showRaw = showRaw;
        this.#socket_init();
        this.notificationContext = notificationContext;
    }

    #socket_init() {
        this.socket = new WebSocket(this.server.replace("http", "ws") + "/ws");
        this.socket.addEventListener("message", event => {
            let json = JSON.parse(event.data);
            let command = json.command;
            let args = json.arguments;
            console.info(json);
            switch (command) {
                case "push_message":
                    if (args.track === this.track) {
                        messageStore.update(msgs => [...msgs, args]);
                        if (this.message_shown(args.track, args.state)) {
                            this.#notify(args);
                        }
                    }
                    break;
                case "set_content":
                    this.#update_msg(args.id, msg => {
                        msg.content = args.content;
                        return msg;
                    });
                    break;
                case "set_state":
                    this.#update_msg(args.id, msg => {
                        if (this.track !== msg.track) {
                            return null;
                        }
                        const prevState = msg.state;
                        msg.state = args.state
                        if (this.message_shown(msg.track, msg.state) && !this.message_shown(msg.track, prevState)) {
                            this.#notify(msg);
                        }
                        return msg;
                    });
                    break;
                case "set_host_message":
                    if (args.track === this.track) {
                        hostMessageStore.set(args["message"])
                    }
                    break;
            }
        });

        this.socket.addEventListener("open", event => {
            this.socket.send(JSON.stringify({"password": this.password}))
            this.#get_all_messages(
                messages => messageStore.set(messages.filter(msg => this.track === msg.track)))
            this.#get_host_message(message => {
                hostMessageStore.set(message)
            })
        })

        this.socket.addEventListener("error", event => console.log(event))

        this.socket.addEventListener("close", () => this.#socket_init())
    }

    #notify(msg) {
        this.notificationContext.addNotification({
            text: `${msg.content}`,
            position: 'bottom-center',
            type: 'default',
            removeAfter: 4000
        })
    }

    #update_msg(id, callable) {
        messageStore.update(_msgs => {
            let msgs = [..._msgs]
            const index = msgs.findIndex(msg => msg.id === id);
            if (index >= 0) {
                const res = callable(msgs[index]);
                if (res === null) {
                    msgs.splice(index, 1);
                } else {
                    msgs[index] = res;
                }
            }
            return msgs;
        })
    }

    #send(command, args) {
        this.socket.send(JSON.stringify({command: command, arguments: args}));
    }

    set_state(id, state) {
        this.#send("set_state", {id: id, state: state})
    }

    set_states(ids, state) {
        ids.forEach(id => this.set_state(id, state));
    }

    set_content(id, content) {
        this.#send("set_content", {id: id, content: content})
    }

    set_host_message(message) {
        this.#send("set_host_message", {track: this.track, message: message})
    }

    message_shown(track, state) {
        return track === this.track && state !== "archived" && (this.showRaw || state !== "raw")
    }

    #get_all_messages(callback) {
        fetch(this.server + "/messages?" + new URLSearchParams({password: this.password}), {
            method: "GET",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        }).then(res => res.json())
            .then(data => callback(data))
    }

    #get_host_message(callback) {
        fetch(this.server + "/host_message?" + new URLSearchParams({password: this.password, track: this.track}), {
            method: "GET",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        }).then(res => res.json())
            .then(data => callback(data["message"]))
    }
}