<script>
    export let unixtime;

    function pad(num) {
        return String(num).padStart(2, "0");
    }
</script>

<span style="color: grey">{pad(new Date(unixtime * 1000).getHours())}:{pad(new Date(unixtime * 1000).getMinutes())}</span>