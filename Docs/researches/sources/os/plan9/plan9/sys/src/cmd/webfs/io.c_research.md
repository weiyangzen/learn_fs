# File Research: sources/os/plan9/plan9/sys/src/cmd/webfs/io.c

This file wraps blocking network and print operations in `Ioproc` calls.

Functions:
- `iovfprint` runs `vfprint` through `iocall`.
- `ioprint` is a varargs wrapper around `iovfprint`.
- `_iotlsdial` dials an address, optionally wraps the fd with `tlsClient`, and returns the TLS fd.
- `iotlsdial` exposes `_iotlsdial` through `iocall`.

TLS behavior:
- Initializes a blank `TLSconn`.
- Contains a commented-out certificate chain read.
- Frees `conn.cert` when present.
- Prints TLS errors to stderr.

Notable risk:
- Certificate checking is explicitly marked as a bug: TLS transport is encrypted but not authenticated here.
