# File Research: sources/os/plan9/9front/sys/src/cmd/lnfs.c

`lnfs` is a user-level 9P filesystem that mounts over a directory and translates long or space-containing names into short filesystem-safe names recorded in `./.longnames`.

Key behavior:
- Runs a 9P server over a pipe and mounts it with `MREPL|MCREATE`; optional `-s` posts the service in `/srv`; `-r` makes it read-only; `-d` logs fcalls.
- Tracks active fids with path strings, open fds, qids, directory-read state, attach ownership, and user.
- Implements 9P `version`, `auth`, `attach`, `walk`, `open`, `create`, `read`, `write`, `clunk`, `remove`, `stat`, and `wstat`.
- Directory reads and stat replies map short underlying names back to long names.
- Creates short names as the first `NAMELEN-1` bytes of base32-encoded MD5 of the long name and appends long names to `.longnames`.
- `readnames()` incrementally reloads `.longnames` based on qid/path and length changes.

Security/authentication is minimal: `rauth()` says auth is not required, and operations generally rely on underlying filesystem permissions plus optional read-only mode.
