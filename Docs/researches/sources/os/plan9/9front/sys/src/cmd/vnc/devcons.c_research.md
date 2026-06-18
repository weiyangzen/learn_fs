# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/devcons.c

## Role

`devcons.c` implements a minimal `/dev/cons`, `/dev/consctl`, and `/dev/snarf` device for the VNC server's private Plan 9 namespace.

## Device Surface

The `consdevtab` exposes:

- Directory root.
- `cons`: writable console output, rendered through `screenputs()`.
- `consctl`: control file placeholder; most behavior is unimplemented.
- `snarf`: shared clipboard buffer.

## Clipboard Handling

- `Snarf snarf` stores the global clipboard buffer, size, and version.
- `setsnarf()` replaces the buffer, increments the version, and updates the directory entry qid version for change detection.
- Opening `snarf` for writing allocates a temporary `Snarf` in `Chan.aux`.
- Closing a write-open snarf file atomically replaces the global snarf buffer with the accumulated data.

## Notable Limitations And Risk Areas

- Reading from `cons` and writing to `consctl` raise placeholder errors.
- `snarf` writes are append-only per open and capped by `MAXSNARF`, but the size check happens before adding the next chunk.
- Ownership and permissions are those supplied through the generic device framework.
