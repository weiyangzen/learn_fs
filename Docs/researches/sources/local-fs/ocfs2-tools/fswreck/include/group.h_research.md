# File Research: sources/local-fs/ocfs2-tools/fswreck/include/group.h

This header declares group descriptor and cluster allocation corruption helpers.

Exports:
- `mess_up_group_minor()`
- `mess_up_group_gen()`
- `mess_up_group_list()`
- `mess_up_cluster_group_desc()`
- `mess_up_cluster_alloc_bits()`

Integration notes:
- Implemented in `group.c`.
- Used by `corrupt_group_desc()`.
