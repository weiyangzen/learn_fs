# File Research: sources/os/plan9/plan9/sys/src/cmd/archfs.c

9P filesystem server that mounts mkfs-style archives.

Key points:
- Reads archive headers containing name, mode, uid, gid, mtime, and length.
- Builds an in-memory 9P file tree with `createpath`.
- Stores archive byte offset/length in per-file `Arch` aux data.
- `fsread` seeks into the archive and reads file contents on demand.
- Main mounts the server at `/mnt/arch` by default, with mount flags from `-a`, `-b`, `-c`, and `-C`.

Dependencies:
- Uses Plan 9 `thread`, `9p`, `bio`, and `Dir` metadata.

Notable behavior:
- Archive parsing stops on literal `end of archive`.
- Directory creation assumes no concurrent tree mutation.
