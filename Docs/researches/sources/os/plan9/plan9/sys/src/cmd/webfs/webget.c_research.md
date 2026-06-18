# File Research: sources/os/plan9/plan9/sys/src/cmd/webfs/webget.c

This is a sample command-line client for `webfs`.

Behavior:
- Opens `<mtpt>/clone`, reads the allocated connection number, writes optional `baseurl`, writes target `url`, optionally writes a post body to `<mtpt>/<conn>/postbody`, opens `<mtpt>/<conn>/body`, and copies it to stdout.
- `xfer` copies from fd to fd in 12 KB chunks and treats read/write errors as fatal.

Options:
- `-b baseurl`
- `-m mtpt`, default `/mnt/web`
- `-p postbody`

Role:
- Demonstrates the expected 9P control protocol for fetching via mounted `webfs`.
