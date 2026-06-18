# File Research: sources/virtualization/nbd/nbdsrv.h

## Purpose
Defines the server-side public data model, flag constants, error domain codes, and shared helper prototypes for NBD server code.

## Main Contents
- `VIRT_STYLE` enumerates export-name virtualization strategies: none, literal IP, IP hash, and CIDR hash.
- `SERVER` stores export configuration, including backing path, expected size, listen address, auth file, export flags, virtualization, hooks, named export, connection limits, transaction log, COW directory, and refcount.
- `CLIENT` stores per-connection state: export size/name, peer address, backend file array, locks, socket, selected server, COW/logging state, negotiated flags, TLS session, and socket callback functions.
- `FILE_INFO` maps an open file descriptor to its export start offset.
- `READ_CTX` tracks fragmented or structured read replies.
- `NBDS_ERRS` enumerates configuration, socket, system, splice, and waitfile validation errors.
- Export flags define read-only, multifile, COW, sparse COW, SDP, sync, flush/FUA/rotational/temporary/trim, fixed-newstyle, treefiles, forced TLS, splice, waitfile, and datalog behavior.

## Dependencies
Includes `lfs.h`, GLib, pthread-related declarations through users, semaphores, sockets, and `nbd.h`.

## Risks and Notes
`SERVER` and `CLIENT` are broad shared structs used across daemon, helper library, and tests. Many fields have manual ownership rules, and several flags interact in mutually exclusive ways that are enforced in `nbd-server.c`.
