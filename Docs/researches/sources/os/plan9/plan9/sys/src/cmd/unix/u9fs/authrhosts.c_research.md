# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/authrhosts.c

Defines Berkeley rhosts-style u9fs authentication.

Behavior:
- `rhostsauth` reports that no auth file exchange is required.
- `rhostsattach` calls `ruserok(remotehostname, 0, rx->uname, rx->uname)` and succeeds only if the host/user is trusted.

Notable comment: the file explicitly calls this weak and only reasonable behind a trusted firewall.
