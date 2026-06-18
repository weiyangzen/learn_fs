# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbidmap.c

Generic numeric id map for SMB fids, tids, and search ids.

Key functions:
- `smbidmapnew` creates a map with free index `-1`.
- `grow` doubles array capacity and links new slots into the free chain.
- `smbidmapadd` allocates an id, stores the pointer, marks slot active with `freechain = -2`, and writes the id into the pointed object’s first `long`.
- `smbidmapfind` validates and returns active id entries.
- `smbidmapremovebyid`, `smbidmapremove`, and `smbidmapremoveif` release ids.
- `smbidmapfree` optionally applies a cleanup callback to active entries.
- `smbidmapapply` iterates active entries.

Interactions:
- Used for session `fidmap`, `tidmap`, and `sidmap`.

Notable details:
- `smbidmapfind` checks `id > m->entries` instead of `id >= m->entries` after decrement, which can allow one-past array access.
