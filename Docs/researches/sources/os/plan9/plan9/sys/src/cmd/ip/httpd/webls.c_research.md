# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/webls.c

Magic helper and standalone tool for HTML directory listings. It loads allow and deny regular expressions from `/sys/lib/webls.allowed` and `/sys/lib/webls.denied`, then permits listings according to those rules while rejecting `..` traversal.

`dols` binds webroot to `/` in magic mode, reads and sorts directory entries, computes formatting widths, renders Plan 9 mode/type/dev/uid/gid/length/mtime fields, links subdirectories back through `/magic/webls?dir=...`, and includes parent navigation only when permitted.
