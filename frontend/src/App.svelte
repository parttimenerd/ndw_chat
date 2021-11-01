<script>
    import { onMount } from 'svelte';
    import { Styles } from 'sveltestrap';
	import Router from 'svelte-spa-router'
	import Moderator from './components/Moderator.svelte'
    import Host from './components/Host.svelte'
    import Home from "./components/Home.svelte"
	export let server_location;

	const routes = {
        // Exact path
        '/': Home,

        // Using named parameters, with last being optional
        '/moderator/:password/:track': Moderator,
        '/host/:password/:track': Host
    }

	let password = ""
    let track = ""


    onMount(() => Home.server_location = server_location)
</script>
<Styles/>
<style>
        html,
    body {
        height: 100%;
    }

    body {
        display: flex;
        align-items: center;
        padding-top: 40px;
        padding-bottom: 40px;
        background-color: #f5f5f5;
    }
</style>
<main>
<Router {routes} />
</main>