<script>
  import Modal from "./lib/Modal.svelte";

  export let onCancel = () => {};
  export let onSubmit = () => {};
  export let cancelText = "Cancel";
  export let submitText = "Submit";
  export let isOpen = false;
  export let title;
  export let reset = () => {};

  function close() {
      isOpen = false;
      reset();
  }
</script>

<style>
	button:focus {
		outline: 5px auto #4D90FE;
  	outline: 5px auto -webkit-focus-ring-color;
	}
</style>

{#key unique}
<Modal bind:open={isOpen}>
    <div class="modal-header">
        <h5 class="modal-title">{title}</h5>
        <!--<button type="button" class="close" on:click={() => (isOpen = false)}>
        <span aria-hidden="true">&times;</span>
        </button>-->
    </div>
    <div class="modal-body"><slot name="content"></slot></div>
      <div class="modal-footer">
        <button type="button" class="btn btn-primary" on:click={() => {onSubmit(); close();}}>{submitText}</button>
        <button type="button" class="btn btn-secondary" data-dismiss="modal" on:click={() => {onCancel(); close();}}>{cancelText}</button>
      </div>
</Modal>

<div class="modal" tabindex="-1" role="dialog">
  <div class="modal-dialog" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">Modal title</h5>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
      <div class="modal-body">

      </div>


    </div>
  </div>
</div>
{/key}