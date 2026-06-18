# sources/user-network-fs/nfs-utils/support/include/nfslib.h

## Purpose
Primary shared support header for nfs-utils, including export entry structures, state path names, qword cache encoding helpers, daemon setup, RPC sockets, and utility prototypes.

## Important APIs, Types, and Functions
Defines `struct state_paths`, `struct sec_entry`, `struct xprtsec_entry`, `struct exportent`, `struct rmtabent`, SEC/XPRTSEC counts, path macros, parser/writer APIs, rmtab APIs, cache qword helpers, daemon helpers, socket helpers, `atomicio()`, and inline `nfs_freeaddrinfo()`.

## Control Flow
Export and rmtab users open parser state, iterate entries, write updates, and close. Cache code qword-encodes strings and integers for procfs channels. Daemons initialize, signal readiness, and create RPC sockets through declared helpers.

## State and Persistence Behavior
Persistent state includes exports, etab, rmtab, and daemon-managed files. `exportent` owns many heap option fields and cached real path data that must be released by export code.

## Dependencies and Integration Points
This header ties together rpcsvc NFS protocol, export flags, uuid, logging, mountd/exportfs parsers, statd state, and generic utility code.

## Risks and Edge Cases
It is broad and ownership-heavy. `exportent` option arrays/strings require disciplined duplication and release. Constants define protocol-visible limits.

## Test Signals
Full nfs-utils build, exports/rmtab parser round trips, qword encoding/decoding tests, daemon socket tests, and memory leak checks around `exportent` duplication/free.
