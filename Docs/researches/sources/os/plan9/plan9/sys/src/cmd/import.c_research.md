# File Research: sources/os/plan9/plan9/sys/src/cmd/import.c

`import.c` mounts a remote exported Plan 9 filesystem.

Key behavior:
- Supports mount flags, old 9P compatibility, authentication disable, encryption selection, AAN filtering, `/srv` posting, passive/backwards mode, and no-tree mode.
- `connect` dials `exportfs`, performs auth (`p9any` or `p9sk2`), sends requested tree, and optionally wraps old servers through `srvold9p`.
- For SSL mode, exchanges random key material, derives two textual secrets from SHA1, optionally runs filter, and calls `pushssl`.
- `passive` authenticates on stdin/stdout as a server-side passive import.
- `filter` reads a remote port, constructs a filtered connection command, forks it, and returns the pipe fd.
- Final fd is mounted at requested mount point or posted in `/srv`.

Important dependencies:
- Uses Plan 9 auth, libsec, network dialing, mount, and namespace APIs.

Notable risks/quirks:
- TLS option exists but fatal-errors as unimplemented.
- Encryption default algorithms are old (`rc4_256 sha1`).
- Timeout is implemented with an alarm note.
