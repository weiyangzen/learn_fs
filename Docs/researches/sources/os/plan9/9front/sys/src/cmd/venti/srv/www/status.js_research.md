# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/www/status.js

`status.js` is a small status-page refresher. It defines a cycle of HTML fragments (`status1.html`, `status2.html`, `status3.html`) and repeatedly advances a hidden frame or location to the next fragment every five seconds.

The script is intended for older browser/frame-based status pages served by Venti’s HTTP interface. All state is global and minimal.
