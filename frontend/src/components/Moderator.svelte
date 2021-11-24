<script>
    import {onMount} from 'svelte';
    import {SERVER_LOCATION} from "../config.js"
    import {messageStore, WebSocketHandler} from "./store.js"
    import Messages from "./Messages.svelte";
    import Page from "./Page.svelte";
    import {getNotificationsContext} from 'svelte-notifications';
    import {password_from_cookie, send_message} from "./util";

    const notificationsContext = getNotificationsContext();

    export let params = {}

    const track = params.track;

    let wsh;

    onMount(() => {
        wsh = new WebSocketHandler(SERVER_LOCATION, password_from_cookie(), track, true, notificationsContext);
    })

</script>

<Page>
    <div slot="title">Moderator of {track}</div>
    <div slot="comm">
        <div class="form-floating">
        <textarea class="form-control" id="floatingTextarea" style="height: max-content"
                  on:keyup={event => wsh.set_host_message(event.target.value)}></textarea>
            <label for="floatingTextarea" style="color: gray">Communicate with Host</label>
        </div>
    </div>
    <div slot="messages">
        <Messages messageStore={messageStore} wsh={wsh} addPassToHostButton=true editable=true
        sendMessage={content => send_message(track, content)}/>
    </div>
</Page>