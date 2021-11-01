<script>
      import {
    Pencil
  } from "svelte-bootstrap-icons";
    import Time from "./Time.svelte";
    import EditableMessage from "./EditableMessage.svelte"
    export let messageStore;
    export let wsh;
    export let addPassToHostButton;
    export let editable = false;
</script>
<div class="bg-white">
    <h6 class="border-bottom border-gray pb-3" style="overflow: fragments">
        <div class="row">
       <div class="col-md-10"> Messages </div>
       <div class="col-md-2"> <span> <button class="btn btn-dark"
                    on:click={wsh.set_states([...$messageStore].filter(msg => wsh.message_shown(msg.track, msg.state)).map(msg => msg.id), 'archived')}>archive all</button></span>
       </div>
        </div>
    </h6>
    <div>
        {#each [...$messageStore] as message}
            {#if wsh.message_shown(message.track, message.state)}
                <div class="pt-1 row pb-3 large border-bottom border-gray">
                    <div class="col-md-1"><Time unixtime={message.time}/></div>
                        {#if editable == "true"}
                            <EditableMessage wsh={wsh} message={message} klass="col-md-9 {message.state === 'visible' && addPassToHostButton === 'true' ? 'bg-success text-white': ''}"/>
                        {:else}
                            <div class="col-md-9 {message.state === 'visible' && addPassToHostButton === 'true' ? 'bg-success text-white': ''}">
                            {message.content}
                            </div>
                        {/if}

                    <div class="col-md-2 align-content-md-center">
                        <div class="btn-group" role="group">
                        {#if addPassToHostButton === "true"}
                            {#if message.state === "visible"}
                                <button class="btn btn-secondary" on:click={wsh.set_state(message.id, 'raw')}>raw
                                </button>
                            {:else}
                                <button class="btn btn-success" on:click={wsh.set_state(message.id, 'visible')}>host
                                </button>
                            {/if}
                        {/if}
                        <button class="btn btn-dark" on:click={wsh.set_state(message.id, 'archived')}>archive</button>
                        </div>
                    </div>
                </div>

                <br>
            {/if}
        {/each}
    </div>
</div>