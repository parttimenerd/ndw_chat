<!-- based on https://getbootstrap.com/docs/5.1/examples/sign-in/ -->
<script>
    import Cookies from 'js-cookie';
    import { onMount } from 'svelte';
    import {check_password, get_tracks} from "./util";

    let password = Cookies.get("password") !== undefined ? Cookies.get("password") : "";
    let track = "";
    let tracks = [];
    let password_correct = false;
    get_tracks(t => {
        tracks = t;
        track = tracks[0];
    });

    onMount(() => {
        check_password(password, success => {
            password_correct = success;
        })
    })

    function handleNewPassword(password) {
        check_password(password, success => {
            password_correct = success;
            if (success) {
                Cookies.set("password", password, { expires: 2, sameSite:'strict' })
            }
        })
    }
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
        <input type="password" class="form-control" id="floatingPassword" bind:value={password} on:input={() => handleNewPassword(password)}>
        <label for="floatingPassword">Password</label>
    </div>
    <a class="w-50 btn btn-primary {!password_correct ? 'disabled' : ''}" href="#/moderator/{track}">Moderator</a><a class="w-50 btn btn-primary {!password_correct ? 'disabled' : ''}" href="#/host/{track}">Host</a>
</div>
