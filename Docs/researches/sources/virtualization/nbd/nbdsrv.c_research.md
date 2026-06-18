# File Research: sources/virtualization/nbd/nbdsrv.c

## Purpose
Provides shared server-side helpers for address matching, client authorization, `SERVER` duplication/refcounting, export size detection, and TRIM/hole-punch handling.

## Main Entry Points
- `address_matches()` checks whether a sockaddr belongs to an address or CIDR mask, including IPv4/IPv6 mapped comparisons.
- `getmaskbyte()` constructs an 8-bit prefix mask.
- `authorized_client()` reads an authorization file and checks the client address against allowed masks.
- `dup_serve()` deep-copies most string fields from a `SERVER`.
- `size_autodetect()` detects export size using `BLKGETSIZE64`, `fstat`, or `lseek(SEEK_END)`.
- `exptrim()` handles NBD TRIM by deleting treefiles or punching holes in backend files.
- `serve_inc_ref()` and `serve_dec_ref()` maintain a global mutex-protected refcount.

## Control Flow
Authorization files are optional; absent or unreadable auth files grant access, while present files are parsed line by line with comments and whitespace stripped. Address matching first parses mask text with `getaddrinfo()`, validates mask length against the client address family, and compares full and partial bytes. Size detection prefers block-device ioctl size, then stat size, then seek-to-end.

## Dependencies
Uses GLib errors/allocation, POSIX networking, file/stat/ioctl/lseek APIs, pthread mutexes, and local `treefiles.h`, `backend.h`, `cliserv.h`, and `nbdsrv.h`.

## Risks and Notes
`authorized_client()` treats an auth file that cannot be opened as allow-all. `serve_dec_ref()` frees only the `SERVER` struct and not dynamically allocated string fields, which is consistent with some call paths but means ownership is delicate. `exptrim()` contains multifile range logic that should be reviewed carefully for cross-file trim ranges.
