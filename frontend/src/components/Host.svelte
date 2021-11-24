<script>
    import {onMount} from 'svelte';
    import {SERVER_LOCATION} from "../config.js"
    import {
        has_quiz,
        hostMessageStore,
        messageStore,
        q_current_question,
        q_current_question_answers,
        q_next_question,
        q_prev_question,
        WebSocketHandler
    } from "./store.js"
    import {ArrowLeft, ArrowRight} from "svelte-bootstrap-icons";
    import Messages from "./Messages.svelte";
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

<Page>
    <div slot="title">Host of {track}</div>
    <div slot="comm">
        <div class="form-floating">
            <textarea class="form-control" id="floatingTextarea" style="height: max-content"
                      disabled="true">{$hostMessageStore}</textarea>
            <label for="floatingTextarea" style="color: gray">Message from Moderator</label>
        </div>
        {#if has_quiz}
            <hr/>
            <div class="row">
                <div class="col-12">
                    {#if wsh !== undefined}
                        <div class="btn-group" role="group">
                            <button class="btn btn-primary"
                                    title="{$q_prev_question === null ? undefined : $q_prev_question.text}"
                                    on:click={() => {wsh.usePrevQuizQuestion()}}>
                                <ArrowLeft></ArrowLeft>
                            </button>
                        </div>
                        <div class="btn-group" role="group">
                            <button class="btn btn-primary"
                                    title="{$q_next_question === null ? undefined : $q_next_question.text}"
                                    on:click={() => {wsh.useNextQuizQuestion()}}>
                                <ArrowRight></ArrowRight>
                            </button>
                        </div>
                    {/if}
                    {#if $q_current_question !== null}
                        <it>Current question:</it> {$q_current_question.text}
                        <span title="Number of answers" class="badge rounded-pill bg-danger translate-middle"
                              style="font-size: 0.7em; margin-left: 1em">
                            {$q_current_question_answers}
                            <span class="visually-hidden">unread messages</span>
                        </span>
                    {/if}
                </div>
            </div>
        {/if}
    </div>
    <div slot="messages">
        <Messages messageStore={messageStore} wsh={wsh} addPassToHostButton=false />
    </div>
</Page>