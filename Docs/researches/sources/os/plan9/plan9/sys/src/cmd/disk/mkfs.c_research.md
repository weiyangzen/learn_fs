# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/mkfs.c

This standalone utility populates a filesystem, directory tree, or archive from proto files.

Key behavior:
- Supports output modes: mounted KFS (`Kfs`), local filesystem destination (`Fs` via `-d`), and archive (`Archive` via `-a`).
- Mounts KFS under `/n/kfs`, sends `allow`, creates/updates `/adm/users`, processes proto files, then sends `disallow` and `sync`.
- Parses indented proto entries into `File` records with destination path, source path, uid, gid, and mode.
- `mkfs` recursively processes proto hierarchy; `mktree` expands `+`/`*` entries from source directories.
- `copyfile` decides metadata, uid/gid behavior, mode overrides, archive output, and whether destination is up-to-date.
- `copy` copies file data, preserving sparse zero ranges by seeking over zero buffers, then atomically renames the temp file through `dirfwstat`.
- `mkdir` creates or updates directories.
- `arch` emits archive headers.
- `setusers` specially handles `/adm` and `/adm/users` before normal population.
- `kfscmd` sends commands to the KFS command channel.

Notable options:
- `-a`: write archive.
- `-d root`: populate ordinary filesystem tree.
- `-n name`: select KFS service name.
- `-p`: update modes even if files are up to date.
- `-r`: force copy as if reaming.
- `-s source`: source root prefix.
- `-u users`: alternate users file.
- `-U`: set uid/gid on ordinary filesystem destination.
- `-x`: emit path/mtime/length listing.
- `-z n`: set copy buffer size.

Notable details:
- `error` attempts to disallow and sync KFS before exiting.
- Environment-variable expansion is supported for proto names beginning with `$`.
