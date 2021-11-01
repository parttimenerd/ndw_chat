<style>
    :global(.comm textarea), :global(.comm span) {
        font-size: 2em;
    }
</style>
<header class="d-flex align-items-center pb-3 mb-5 border-bottom">
    <span href="/" class="d-flex align-items-center text-dark text-decoration-none">
        <span class="fs-4"><slot name="title"></slot></span>
    </span>
</header>
<div class="col-lg-7 mx-auto p-3 py-md-5 page">
    <div class="row g-5">
      <div class="col-md-12 comm">
    <slot name="comm"></slot>
      </div>
        <div class="col-md-12">
    <slot name="messages"></slot>
            </div>
      </div>
</div>
