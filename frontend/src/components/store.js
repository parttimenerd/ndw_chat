import {writable,} from 'svelte/store';
import {check_password} from "./util";
import {push} from "svelte-spa-router";

export let hostMessageStore = writable("");
export let messageStore = writable([]);
// [{"user": {pseudonym, email}, "score": float}]
export let q_scores = writable([]); // ordered descending by score
// [{"question": question, "count": count}] // ordered ascending by question.id
export let q_answer_count = writable([]);
// {question_id: {track, slot, text, id}}
export let q_questions = writable({});
export let has_quiz = writable(false);

export let q_current_question = writable(null);
export let q_current_question_answers = writable(0);
export let q_prev_question = writable(null);
export let q_next_question = writable(null);

export class WebSocketHandler {
    constructor(server, password, track, showRaw, notificationContext) {
        this.server = server;
        this.password = password;
        this.track = track;
        this.showRaw = showRaw;
        this.#socket_init();
        this.notificationContext = notificationContext;
        this.prevQuestionId = -1;
        this.nextQuestionId = -1;
        this.currentQuestionId = -1;
        this.quizAnswerCounts = {};
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
                        hostMessageStore.set(args["message"]);
                    }
                    break;
                case "scores":
                    let {scores: scores, count: count, questions: questions} = args;
                    q_scores.set(scores);
                    const questionIds = Object.keys(count)
                    q_answer_count.set(questionIds.sort().map(i => {
                        return {"question": questions[i], "count": count[i]};
                    }));
                    this.quizAnswerCounts = count;
                    q_questions.set(questions);
                    this.#update_current_question_answers();
                    break;
                case "has_quiz":
                    has_quiz.set(true);
                    break;
                case "set_current_question":
                    if (args.track === this.track) {
                        let {current: current, prev: prev, next: next} = args["question"];
                        q_current_question.set(current);
                        q_next_question.set(next);
                        this.prevQuestionId = prev == null ? -1 : prev.id;
                        this.nextQuestionId = next == null ? -1 : next.id;
                        this.currentQuestionId = current == null ? -1 : current.id;
                        q_prev_question.set(prev);
                        this.#update_current_question_answers();
                    }
            }
        });

        this.socket.addEventListener("open", event => {
            check_password(this.password, (success) => {
                if (!success) {
                    push("/");
                }
                this.socket.send(JSON.stringify({"password": this.password}))
                if (this.track.length !== "") {
                    this.#get_all_messages(
                        messages => messageStore.set(messages.filter(msg => this.track === msg.track)))
                    this.#get_host_message(message => {
                        hostMessageStore.set(message)
                    })
                }
            })
        })

        this.socket.addEventListener("error", event => console.log(event))

        this.socket.addEventListener("close", () => setTimeout(() => this.#socket_init(), 20))
    }

    #update_current_question_answers() {
        if (this.currentQuestionId !== -1) {
            q_current_question_answers.set(this.quizAnswerCounts[this.currentQuestionId]);
        } else {
            q_current_question_answers.set(0);
        }
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
        console.info(`send ${command}: ${JSON.stringify(arguments)}`,);
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

    usePrevQuizQuestion() {
        this.#send("set_current_question", {track: this.track, question_id: this.prevQuestionId})
    }

    useNextQuizQuestion() {
        this.#send("set_current_question", {track: this.track, question_id: this.nextQuestionId})
    }
}