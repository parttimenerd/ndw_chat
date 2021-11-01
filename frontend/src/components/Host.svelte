<script>
    import {onMount} from 'svelte';
    import {SERVER_LOCATION} from "../config.js"
    import {messageStore, hostMessageStore, WebSocketHandler} from "./store.js"
    import Messages from "./Messages.svelte";
    import Page from "./Page.svelte";
    import { getNotificationsContext } from 'svelte-notifications';
    const notificationsContext = getNotificationsContext();

    export let params = {}

    const track = params.track
    const password = params.password

    let wsh;

    onMount(() => {
        wsh = new WebSocketHandler(SERVER_LOCATION, password, track, false, notificationsContext);
    })

</script>

<Page>
    <div slot="title">Host of {track}</div>
    <div slot="comm">
        <div class="form-floating">
        <textarea class="form-control" id="floatingTextarea" style="height: max-content" disabled="true">{$hostMessageStore}</textarea>
            <label for="floatingTextarea" style="color: gray">Message from Moderator</label>
        </div>
    </div>
    <div slot="messages">
        <Messages messageStore={messageStore} wsh={wsh} addPassToHostButton=false />
    </div>
</Page>