<script>
    import {link} from 'svelte-spa-router';
    let scrollY;
    let headerOffsetTop;
</script>
<style>
    :global(.comm textarea), :global(.comm span) {
        font-size: 2em;
    }
</style>

<svelte:window bind:scrollY={scrollY}></svelte:window>


<div style="max-height: 100%">
    <div bind:offsetHeight={headerOffsetTop} style="z-index: 3; position: fixed !important; top: 0px; padding-top: 6px !important; !important; width: 100%; background: #ffffffdf">
        <header class="d-flex align-items-center pb-1 mb-1 border-bottom">
            <span class="d-flex align-items-center text-dark text-decoration-none">
                <span class="fs-4"><a use:link href="/">Hmm?</a></span>
                <span class="fs-1" style="width: 1em"></span>
                <span class="fs-4"><slot name="title"></slot></span>
            </span>
        </header>
        <div class="col-lg-7 mx-auto p-3 py-md-5 page" style="height: 100%;">
            <div class="row g-5">
                <div class="col-md-12 comm">
                    <slot name="comm"></slot>
                </div>
            </div>
        </div>
    </div>
    <div style="height: {headerOffsetTop}px"></div>
    <div class="col-lg-7 mx-auto p-3 py-md-5 page" style="height: 100%; padding-top: 0 !important;">
        <div class="row g-5">
            <div class="col-md-12" style="height: 300px">
                <slot name="messages"></slot>
            </div>
        </div>
    </div>
</div>
