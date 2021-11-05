<script>
    import { onMount } from 'svelte';
    import { Styles } from 'sveltestrap';
	import Router from 'svelte-spa-router'
	import Moderator from './components/Moderator.svelte'
    import Host from './components/Host.svelte'
    import Home from "./components/Home.svelte"
    import Notifications from 'svelte-notifications';
	export let server_location;

	const routes = {
        // Exact path
        '/': Home,

        // Using named parameters, with last being optional
        '/moderator/:track': Moderator,
        '/host/:track': Host
    }

	let password = ""
    let track = ""


    onMount(() => Home.server_location = server_location)
</script>
<Styles/>
<style>

    body {
        display: flex;
        align-items: center;
        background-color: #f5f5f5;
    }
</style>
<Notifications>
    <main>
    <Router {routes} />
    </main>
</Notifications>