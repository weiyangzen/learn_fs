# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/net.c

Purpose: User-mode network listener layer for cwfs 9P service connections.

Key behavior:
- `annstrs[]` holds announce strings gathered from `main.c -a`.
- `netinit()` announces each configured network address and records announce/listen directories.
- `netstart()` starts one `neti` process per announced network.
- `neti()` loops on `listen()`/`accept()`, obtains remote address info with `getnetconninfo()`, and hands accepted fds to `srvchan()`.

Context:
- Comments explain the shift from the old kernel fileserver’s Ethernet/IL packet queues to user-mode per-connection stream handling.
- Actual 9P message framing is handled by `srv.c`, not here.
