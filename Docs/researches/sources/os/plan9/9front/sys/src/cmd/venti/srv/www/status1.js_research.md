# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/www/status1.js

`status1.js` is a variant of the status-page auto-rotator. It maintains a list of status HTML page names and replaces `parent.status.location.href` with the next page every five seconds.

It is tightly coupled to a frameset layout with a frame named `status`. Like `status.js`, it is simple global JavaScript for the Venti web UI.
