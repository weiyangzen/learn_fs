# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/netlib_history.c

Netlib history magic helper. It parses `file` and optional `diff` query fields, rejects parent-directory traversal and oversized names, changes into `/usr/web/historic`, then walks backward through dated snapshots to list historical versions.

In diff mode it limits the result count, gunzips `.gz` snapshots into temporary files, runs `diff -nb` between adjacent versions, and embeds the diff output in HTML. HEAD requests emit headers without a body.
