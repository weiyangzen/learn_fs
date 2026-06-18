# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/save.c

Magic helper for simple web form logging. GET uses the query string and POST reads the request body, truncates at the first newline, caps each logged request at 24 KiB, and appends `at <time> <data>` to `/usr/web/save/<uri>.data`.

It serves `/usr/web/save/<uri>.html` as the response through `sendfd`. The `.data` file can use exclusive-use mode; `openLocked` retries briefly when the file is locked to avoid interleaved appends.
