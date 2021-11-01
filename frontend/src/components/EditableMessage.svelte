<script>
    import {onMount} from 'svelte';
    import Pencil from "svelte-bootstrap-icons/lib/Pencil";
    export let message;
    export let klass;
    export let wsh;
    let currentlyInEditMode = false;
    let currentText = wsh;
    onMount(() => {
        currentText = message.content;
    })
</script>
{#if currentlyInEditMode === true}
    <div class="{klass}">
        <textarea style="width: 100%" bind:value={currentText}/>
        <div class="btn-group" role="group">
            <button class="btn btn-success" on:click={event => {wsh.set_content(message.id, currentText); currentlyInEditMode = false}}>Submit Change</button>
            <button class="btn btn-dark" on:click={() => currentlyInEditMode = false}>Cancel</button>
        </div>
    </div>
{:else}
    <div on:click|once={() => currentlyInEditMode = true} class="{klass}" >
        {message.content}
    </div>
{/if}

