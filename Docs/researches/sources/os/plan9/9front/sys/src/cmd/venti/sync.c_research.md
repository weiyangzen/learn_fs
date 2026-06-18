# File Research: sources/os/plan9/9front/sys/src/cmd/venti/sync.c

`venti/sync` is a client utility that connects to a Venti server and sends `vtsync()`. It accepts an optional `-h host` and a hidden/test `-x` mode that connects and disconnects without syncing.

It installs Venti formatters, dials, performs protocol connect, optionally syncs, then hangs up. It is the client-side counterpart to the server’s `VtTsync` handling.
