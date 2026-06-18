# File Research: sources/os/plan9/9front/sys/src/cmd/venti/write.c

`venti/write` reads one block from stdin, optionally zero-truncates it, writes it to a Venti server with a selected block type, prints the resulting score, and disconnects.

It enforces `VtMaxLumpSize`, accepts `-h host`, `-t type`, and `-z`, and uses libventi’s `vtwrite()`/`vtdial()`/`vtconnect()` APIs. This is the simple command-line client for adding a block to a Venti store.
