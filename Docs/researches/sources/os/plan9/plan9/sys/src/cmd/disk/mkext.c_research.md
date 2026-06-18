# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/mkext.c

This standalone utility extracts or transforms mkfs-style archive streams.

Key behavior:
- Reads archive headers with fields: filename, mode, uid, gid, mtime, bytes.
- Stops on `end of archive`.
- Options support destination prefix (`-d`), header-only output (`-h`), uid/gid restoration (`-u`), time restoration (`-T`), and verbose mode (`-v`).
- `selected` filters extraction to requested file prefixes.
- `mkdirs` creates parent directories for selected extraction.
- `mkdir` creates directories and applies mode, uid/gid, and mtime as requested.
- `extract` writes file contents and then applies metadata.
- `seekpast` skips unselected file payloads.
- `warn` reports recoverable metadata/write issues; `error` exits on fatal archive errors.

Role:
- Companion to `mkfs -a` archive output.
