import logging
import statistics
import time
from dataclasses import dataclass, field
from random import random
from typing import Optional, List, Dict, Set

import yaml
from dataclasses_json import dataclass_json  #
from email_validator import validate_email, EmailNotValidError
from tinydb import Query

from ndw_chat.db import db
from ndw_chat.util import base_path, config


@dataclass_json
@dataclass
class QuizUser:
    id: int
    pseudonym: str
    email: str
    time: float


@dataclass_json
@dataclass
class QuizAnswer:
    answer: str
    question: int
    user: int
    time: float


@dataclass_json
@dataclass
class QuizQuestion:
    track: str
    slot: int
    text: str
    estimation: Optional[str]
    estimation_solution: Optional[float]
    choice: Optional[List[str]]
    choice_solution: Optional[str]
    id: int = -1


@dataclass_json
@dataclass
class Quiz:
    questions: List[QuizQuestion] = field(default_factory=lambda: [QuizQuestion("room1", 1,
                                                                                "estimation question",
                                                                                "years",
                                                                                10,
                                                                                None,
                                                                                None),
                                                                   QuizQuestion("room1", 2, "choice", None, None,
                                                                                ["A", "B", "C"], "A")])


@dataclass_json
@dataclass
class QuizUserScore:
    user: QuizUser
    score: float


@dataclass_json
@dataclass
class QuizUserScores:
    scores: List[QuizUserScore]
    """ first has largest score """
    count: Dict[int, int]
    """ id → answers """
    questions: Dict[int, QuizQuestion]


QUIZ_FILE = "quiz.yaml"
_quiz: Optional[Quiz] = None


def quiz() -> Quiz:
    global _quiz
    if _quiz:
        return _quiz
    quiz_file = base_path() / QUIZ_FILE
    if quiz_file.exists():
        with quiz_file.open() as f:
            _quiz = Quiz.from_dict(yaml.safe_load(f))
            for i, question in enumerate(_quiz.questions):
                question.id = i
                assert (question.estimation is None) ^ (question.choice is None)
            return _quiz
    else:
        with quiz_file.open("w") as f:
            yaml.dump(Quiz().to_dict(), f)
            print(f"Please update the template quiz file at {quiz_file}")
        exit(0)


def get_registered_users() -> List[QuizUser]:
    return [QuizUser.from_dict(user) for user in db("quiz_users")]


def register_user(pseudonym: str, email: str) -> Optional[int]:
    """ Registers user (if needed) and returns its id or None """
    if not pseudonym or not email:
        return -1
    if len(pseudonym + email) > 1000:
        return -1
    for user in get_registered_users():
        if (user.pseudonym == pseudonym) ^ (user.email == email):
            return None
        if user.pseudonym == pseudonym and user.email == email:
            return user.id
    try:
        email = validate_email(email).email
        id = len(db("quiz_users")) + int(random() * 1000) + 1
        db("quiz_users").insert(QuizUser(id, pseudonym, email, time.time()).to_dict())
        logging.info(f"registered quiz user {pseudonym} ({email})")
        return id
    except EmailNotValidError as e:
        logging.info(f"email address {email} invalid: {e}")
        return None


def get_user(id: int) -> Optional[QuizUser]:
    val = db("quiz_users").search(Query().id == id)
    if val:
        return QuizUser.from_dict(val[0])
    return None


def get_questions() -> List[QuizQuestion]:
    return quiz().questions


def get_answers() -> List[QuizAnswer]:
    return [QuizAnswer.from_dict(user) for user in db("quiz_answers")]


def answered(user_id: int, question_id: int) -> bool:
    return any(answer.question == question_id and user_id == answer.user for answer in get_answers())


def add_answer(user_id: int, question_id: int, answer: str) -> Optional[QuizAnswer]:
    if len(answer) > 1000 or len(answer) < 1:
        return None
    if answered(user_id, question_id):
        return None
    if get_user(user_id) is None or all(question.id != question_id for question in get_questions()):
        return None
    if all(q.id != question_id for q in get_current_questions() if is_current_question_enabled(q.track)):
        return None
    answer = QuizAnswer(question=question_id, user=user_id, answer=answer, time=time.time()).to_dict()
    db("quiz_answers").insert(answer)
    logging.info(f"answer of user {user_id} to question {question_id}")
    return answer


def get_question(id: int) -> Optional[QuizQuestion]:
    if 0 <= id < len(quiz().questions):
        return quiz().questions[id]
    return None


def get_current_question(track: str) -> Optional[QuizQuestion]:
    val = db("current_questions").search(Query().track == track)
    if val:
        return get_question(val[0]["id"])
    return None


def get_current_questions() -> List[QuizQuestion]:
    return [get_current_question(t.name) for t in config().tracks if get_current_question(t.name)]


def get_question_for_slot(track: str, slot: int) -> Optional[QuizQuestion]:
    return ([q for q in get_questions() if q.track == track and q.slot == slot] + [None])[0]


def get_next_question(track: str) -> Optional[QuizQuestion]:
    cur = get_current_question(track)
    if cur:
        return get_question_for_slot(track, cur.slot + 1)
    return get_question_for_slot(track, 0) or get_question_for_slot(track, 1)


def get_prev_question(track: str) -> Optional[QuizQuestion]:
    cur = get_current_question(track)
    if cur:
        return get_question_for_slot(track, cur.slot - 1)
    return None


def set_current_question(track: str, question_id: int):
    if get_question(question_id) or question_id == -1:
        db("current_questions").upsert({"track": track, "id": question_id}, Query().track == track)
        enable_current_question(track, False)


def enable_current_question(track: str, enabled: bool):
    db("current_question_enabled").upsert({"track": track, "enabled": enabled}, Query().track == track)


def is_current_question_enabled(track: str) -> bool:
    val = db("current_question_enabled").search(Query().track == track)
    if val:
        return val[0]["enabled"]
    return False


def parse_float(text: str) -> float:
    try:
        return float(text)
    except ValueError:
        return float("-inf")


def get_slots() -> Set[int]:
    return {q.slot for q in get_questions()}


def count_answers(question_id: int) -> int:
    return db("quiz_answers").count(Query().question_id == question_id)


def user_scores() -> QuizUserScores:
    count: Dict[int, int] = {q.id: 0 for q in get_questions()}
    all_answers_per_q: Dict[int, List[float]] = {}
    for answer in get_answers():
        question = get_question(answer.question)
        if question.estimation:
            if question.id not in all_answers_per_q:
                all_answers_per_q[question.id] = []
            all_answers_per_q[question.id].append(parse_float(answer.answer))
        count[answer.question] += 1

    all_answers_per_q_ranked: Dict[int, Dict[float, float]] = {}  # question → answer → score
    for question, answers in all_answers_per_q.items():
        q = get_question(question)
        answers = sorted(answers, key=lambda v: abs(q.estimation_solution - v))
        all_answers_per_q_ranked[question] = {v: 2 / (i + 2) for i, v in enumerate(answers)}

    users: Dict[int, Dict[int, Dict[str, float]]] = {}  # user → slot → track → points
    slots = get_slots()
    for answer in get_answers():
        question = get_question(answer.question)
        if answer.user not in users:
            users[answer.user] = {slot: {t.name: 0 for t in config().tracks} for slot in slots}
        if question.estimation:
            users[answer.user][question.slot][question.track] = all_answers_per_q_ranked[answer.question][
                parse_float(answer.answer)]
        else:
            users[answer.user][question.slot][question.track] = 1 if question.choice_solution == answer.answer else 0
    mean_users: List[QuizUserScore] = []
    for user, user_d in users.items():
        summed = 0
        for slot, d in user_d.items():
            if d:
                summed += statistics.mean(d.values())
        mean_users.append(QuizUserScore(get_user(user), summed))

    return QuizUserScores(sorted(mean_users, key=lambda u: u.score, reverse=True), count,
                          {q.id: q.to_dict() for q in get_questions()})


def delete_old_users_and_answers():
    for table in ["quiz_answers", "quiz_users"]:
        db(table).remove(Query().time <= time.time() - config().delete_after_days * 24 * 60 * 60)
