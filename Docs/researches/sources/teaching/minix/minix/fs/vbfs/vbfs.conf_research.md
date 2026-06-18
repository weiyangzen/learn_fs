# File Research: sources/teaching/minix/minix/fs/vbfs/vbfs.conf

Service configuration for the `vbfs` filesystem server.

Key contents:
- Declares `service vbfs`.
- Allows IPC with `SYSTEM`, `pm`, `vfs`, `rs`, `ds`, `vm`, and `vbox`.
- Grants VM calls:
  - `SETCACHEPAGE`
  - `CLEARCACHE`

This matches VBFS’s use of SFFS/fsdriver infrastructure and VirtualBox backend access.
