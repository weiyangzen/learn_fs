# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/save.c

Magic helper for simple form logging. GET uses the query string, POST reads the request body after optional `100 Continue`, truncates at the first newline, caps each entry at 24 KiB, and appends `at <time> <data>` to `/usr/web/save/<uri>.data`.

It serves `/usr/web/save/<uri>.html` as the response through `sendfd`. Data files may use Plan 9 exclusive-use locking; `openLocked` retries briefly when files are locked to avoid interleaved appends.
