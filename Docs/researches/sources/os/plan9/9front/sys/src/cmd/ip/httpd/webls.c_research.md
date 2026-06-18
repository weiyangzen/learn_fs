# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/webls.c

Magic helper and standalone tool for HTML directory listings. It loads allow/deny regexes from `/sys/lib/webls.allowed` and `/sys/lib/webls.denied`, then lists only permitted directories.

`dols` binds webroot to `/` in magic mode, reads and sorts directory entries, formats Plan 9 mode/type/dev/uid/gid/length/mtime fields, links subdirectories back through `/magic/webls?dir=...`, and includes parent navigation only when permitted.
