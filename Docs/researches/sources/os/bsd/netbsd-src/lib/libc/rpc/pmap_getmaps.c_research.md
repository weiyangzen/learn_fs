# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/pmap_getmaps.c

Read completely: 107 lines.

Implements `pmap_getmaps()`, which contacts the remote portmapper over TCP at `PMAPPORT`, calls `PMAPPROC_DUMP`, and decodes the returned `struct pmaplist` with `xdr_pmaplist()`.

It uses a 60-second timeout, creates a temporary TCP client with `clnttcp_create()`, prints client errors with `clnt_perror()`, destroys the client, and restores the input address port to zero before returning.

This is a legacy v2 portmapper query path. Returned map list ownership follows XDR allocation conventions and must be freed by callers with the matching XDR free path.
