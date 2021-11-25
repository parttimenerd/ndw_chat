

let quizzes = {};

class QuizState {
    constructor(track, element) {
        this.element = element
        this.track = track
        /** question dict or undefined,
         * class QuizQuestion:
                track: str
                slot: int
                text: str
                estimation: Optional[str]
                estimation_solution: Optional[float]
                choice: Optional[List[str]]
                choice_solution: Optional[str]
                id: int = -1
         */
        this.current_question = null
        this.user_id = localStorage.getItem("user_id")
        this.registered = this.user_id != null;
    }

    setUserId(user_id) {
        this.user_id = user_id;
        this.registered = this.user_id != null;
    }

    child(element_class) {
        if (element_class === "quiz") {
            return this.element
        }
        return this.element.querySelector("." + element_class)
    }

    hide(element_class) {
        this.child(element_class).style.display = "none"
    }

    show(element_class) {
        this.child(element_class).style.display = "block"
    }

    enable(button_class) {
        this.child(button_class).disabled = false
    }

    disable(button_class) {
        this.child(button_class).disabled = true
    }


    updateUI() {
        if (this.current_question != null) {
            this.show("quiz")
            if (this.registered) {
                this.hide("register")
                this.enable("submit_answer")
                this.hide("open_register_button")
            } else {
                if (this.needsToRegister) {
                    this.show("register")
                    this.disableSubmitButton()
                }
            }
        } else {
            this.hide("quiz")
        }
    }

    renderCurrentQuestion() {
        if (this.current_question === null) {
            return;
        }
        this.element.querySelector(".question").textContent = this.current_question.text
        let answer_element = this.element.querySelector(".answer")
        let estimation = this.current_question.estimation
        let choice = this.current_question.choice
        answer_element.innerHTML = "";
        if (estimation != null) {
            let input_element = document.createElement("input")
            input_element.type = "number"
            input_element.step = "any"
            let label_element = document.createElement("label")
            label_element.textContent = estimation
            answer_element.appendChild(input_element)
            answer_element.appendChild(label_element)
        } else {
            let name = this.track;
            let html = ""
            let i = 0
            for (const choiceElement of choice) {
                let id = `${this.track}_${i}`;
                html += `<div>
                <input type="radio" id="${id}" name="${name}" value="${choiceElement}">
                    <label for="${id}">${choiceElement}</label>
            </div>\n`;
                i++
            }
            answer_element.innerHTML = html
        }
    }

    fetch_current_question() {
        this.fetch("unanswered_question", {}, res => {
            if (JSON.stringify(this.current_question) !== JSON.stringify(res["question"])) {
                this.current_question = res["question"]
                this.fetch("user_registered", {"user_id": this.user_id}, res => {
                    this.registered = res["registered"]
                    this.renderCurrentQuestion()
                    this.updateUI()
                })

            }
        })
    }

    register(pseudonym, email) {
        this.fetch("register_quiz_user", {"pseudonym": pseudonym, "email": email}, res => {
            if (res.success) {
                this.user_id = res["user_id"]
                localStorage.setItem("user_id", this.user_id)
                this.registered = true
                this.needsToRegister = false
                for (const quiz of Object.values(quizzes)) {
                    quiz.setUserId(this.user_id);
                }
                this.updateUI()
            } else {
                console.log(res);
            }
        })
    }

    handle_register() {
        this.register(this.element.querySelector(".pseudonym").value, this.element.querySelector(".email").value)
    }

    handle_submit_answer() {
        if (this.current_question != null && this.registered) {
            if (this.current_question["estimation"]) {
                this.submit_answer(this.element.querySelector(".answer input").value)
            } else {
                let selectedElem = this.element.querySelector('input[type="radio"]:checked');
                if (selectedElem !== null) {
                    this.submit_answer(selectedElem.value)
                }
            }
        }
    }

    submit_answer(answer) {
        if (this.current_question != null) {
            this.fetch("submit_quiz_answer", {
                "question_id": this.current_question.id,
                "answer": answer
            }, res => {
                if (res["already_answered"] || res["success"]) {
                    this.current_question = null
                    this.updateUI()
                }
            })
        }
    }

    fetch(path, query, onsuccess) {
        query["track"] = this.track
        if (this.user_id != null) {
            query["user_id"] = this.user_id
        }
        fetch(`${NDW_CHAT_SERVER_URL}/${path}?${new URLSearchParams(query)}`, {
            method: "GET",
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            }
        }).then(res => {
             res.json().then(onsuccess)
        })
    }
}

function init_submit_question(element, track) {
    element.querySelector(".submit_question").addEventListener("click", () => {
        fetch(NDW_CHAT_SERVER_URL + "/send", {
            method: "POST",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                "track": track,
                "content": element.querySelector("textarea").value
            })
        }).then(() => {
            element.querySelector(" .ndw_chat_successful").style.display = "block";
            setTimeout(() => element.querySelector(" .ndw_chat_successful").style.display = "none", 3000);
            element.querySelector("textarea").value = ""
        })
    });
}

function init_quiz(element, track) {
    let quiz = new QuizState(track, element.querySelector(".quiz"));
    quiz.fetch_current_question();
    quizzes[track] = quiz
    element.querySelector(".submit_answer").addEventListener("click", () => {
        quiz.handle_submit_answer()
    })
    element.querySelector(".register_button").addEventListener("click", () => {
        quiz.handle_register()
    })
    element.querySelector(".open_register_button").addEventListener("click", () => {
        quiz.show("register");
        quiz.disable("open_register_button");
    })
    setInterval(() => quiz.fetch_current_question(), 5_000)
}

document.querySelectorAll(".ndw_chat").forEach(element => {
    let track = element.getAttribute("track");
    init_submit_question(element, track);
    init_quiz(element, track);
});