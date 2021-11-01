import App from './App.svelte';
import {SERVER_LOCATION} from "./config";

const app = new App({
	target: document.body,
	props: {
		server_location: SERVER_LOCATION
	}
});

export default app;