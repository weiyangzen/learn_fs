# File Research: sources/os/plan9/9front/sys/src/cmd/lp/ipcopen.c

`ipcopen` connects stdin/stdout to a dialed network service. It builds a Plan 9 net address from destination, network, and service, dials it, opens the connection’s `data` file for read and write, then forks bidirectional copy loops.

The child copies remote data to stdout, while the parent copies stdin to remote. Each side calls `hangup()` and closes fds when done. A single leading NUL byte from remote is treated as an immediate termination condition in `pass()`.

This is simple datakit/network plumbing for older lp workflows.
