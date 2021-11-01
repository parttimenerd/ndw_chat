<!-- based on https://getbootstrap.com/docs/5.1/examples/sign-in/ -->
<script>
    import {get_tracks} from "./util";

    let password = "";
    let track = "";
    let tracks = [];
    get_tracks(t => tracks = t);
</script>

<style>

    .main {
        width: 100%;
        max-width: 330px;
        padding: 15px;
        margin: auto;
    }

    .form-floating:focus-within {
        z-index: 2;
    }

    input[type="password"] {
        margin-bottom: 10px;
        border-top-left-radius: 0;
        border-top-right-radius: 0;
    }

    a:visited {
         color: white !important;
     }
</style>

<div class="main text-center">
    <h1 class="h3 mb-3 fw-normal">Hmm?</h1>

    <div class="form-floating">
        <select class="custom-select form-control" id="floatingInput" bind:value={track}>
            {#each tracks as t}
                <option value="{t}">{t}</option>
            {/each}
        </select>
        <label for="floatingInput">Track</label>
    </div>
    <div class="form-floating">
        <input type="password" class="form-control" id="floatingPassword" bind:value={password}>
        <label for="floatingPassword">Password</label>
    </div>
    <a class="w-50 btn btn-primary" href="#/moderator/{password}/{track}">Moderator</a><a class="w-50 btn btn-primary" href="#/host/{password}/{track}">Host</a>
</div>
