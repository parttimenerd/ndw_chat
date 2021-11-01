<script>
    import Time from "./Time.svelte";
    export let messageStore;
    export let wsh;
    export let addPassToHostButton;
</script>
<div class="bg-white">
    <h6 class="border-bottom border-gray pb-3" style="overflow: fragments">
        Messages
        <span style="float: right; margin-left: auto; margin-right: 0"> <button class="btn btn-dark"
                    on:click={wsh.set_states([...$messageStore].filter(msg => wsh.message_shown(msg.track, msg.state)).map(msg => msg.id), 'archived')}>archive all</button></span>
    </h6>
    <div>
        {#each [...$messageStore].reverse() as message}
            {#if wsh.message_shown(message.track, message.state)}
                <div class="pt-1 row pb-3 large border-bottom border-gray">
                    <div class="col-md-1"><Time unixtime={message.time}/></div>
                    {#if message.state === "visible" && addPassToHostButton === "true"}
                        <div class="col-md-8" style="color: darkgreen">{message.content}</div>
                    {:else}
                        <div class="col-md-8">{message.content}</div>
                    {/if}

                    <div class="col-md-3 align-content-md-center">
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

                <br>
            {/if}
        {/each}
    </div>
</div>