<script>
    import {onMount} from 'svelte';
    import {SERVER_LOCATION} from "../config.js"
    import {q_answer_count, q_scores, WebSocketHandler} from "./store.js"
    import Page from "./Page.svelte";
    import {getNotificationsContext} from 'svelte-notifications';
    import {password_from_cookie} from "./util";

    const notificationsContext = getNotificationsContext();

    export let params = {}

    const track = params.track;

    let wsh;

    onMount(() => {
        wsh = new WebSocketHandler(SERVER_LOCATION, password_from_cookie(), track, false, notificationsContext);
    })

</script>

<Page withoutModeratorText={true}>
    <div slot="title">Quiz Scores</div>
    <div slot="messages">
        <div class="row">
            <div class="col-4">
                <h3>Scores</h3>
                <table class="table">
                    <thead>
                    <tr>
                        <th scope="col">#</th>
                        <th scope="col">User</th>
                        <th scope="col">Score</th>
                    </tr>
                    </thead>
                    <tbody>
                    {#each [...$q_scores] as score_dict, i}
                        <tr>
                            <td scope="row">{i}</td>
                            <td><a href="mailto:{score_dict.user.email}">{score_dict.user.pseudonym}</a></td>
                            <td>{score_dict.score.toFixed(2)}</td>
                        </tr>
                    {/each}
                    </tbody>
                </table>
            </div>
            <div class="col-8">
                <h3>Answers</h3>
                <table class="table">
                    <thead>
                    <tr>
                        <th scope="col">Slot</th>
                        <th scope="col">Track</th>
                        <th scope="col">Question</th>
                        <th scope="col">Answers</th>
                    </tr>
                    </thead>
                    <tbody>
                    {#each [...$q_answer_count].sort((x, y) => x.question.slot - y.question.slot) as count_dict}
                        <tr>
                            <td>{count_dict.question.slot}</td>
                            <td>{count_dict.question.track}</td>
                            <td>{count_dict.question.text}</td>
                            <td>{count_dict.count}</td>
                        </tr>
                    {/each}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</Page>