# File Research: sources/os/plan9/plan9/sys/src/cmd/webfsget.c

This is another example client for mounted `webfs`, essentially equivalent to `webfs/webget.c`.

Behavior:
- Opens `/mnt/web/clone` or custom mount point.
- Reads connection number from clone.
- Writes optional `baseurl` and required `url` to the clone ctl fd.
- Optionally writes POST data to the connection's `postbody`.
- Opens the connection's `body` and streams it to stdout.

Options:
- `-b baseurl`
- `-m mtpt`
- `-p postbody`

Role:
- A top-level example command showing how to drive the webfs 9P interface.
