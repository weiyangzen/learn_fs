# File Research: sources/local-fs/squashfs-tools/squashfs-tools/virt_disk_pos.h

Header for physical and virtual output position management in `mksquashfs`.

Defines inline helpers for:
- Physical disk position: `set_dpos()`, `get_dpos()`, `get_and_inc_dpos()`, and aligned increment for `struct file_buffer`.
- Virtual position: `set_vpos()`, `get_vpos()`, `get_and_inc_vpos()`, `inc_vpos()`, `mark_vpos()`, `unmark_vpos()`, `get_marked_vpos()`, `is_vpos_marked()`.
- Combined position reset with `set_pos()`.

Marker semantics:
- `marked_vpos == 0` means no saved write position.
- `marked_vpos == 1` means mark requested but no increment has captured the previous value yet.
- Other values are saved virtual positions.

Also defines the virtual/disk hash table size, hash macro, `struct virt_disk`, and prototypes for map operations implemented in `virt_disk_pos.c`.
