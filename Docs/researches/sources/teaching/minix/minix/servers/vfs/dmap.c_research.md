# File Research: sources/teaching/minix/minix/servers/vfs/dmap.c

This file owns the character/block device major-to-driver map.

Key state:
- Global `struct dmap dmap[NR_DEVICES]`.

Key functions:
- `lock_dmap` / `unlock_dmap`: lock per-driver map entries while preserving worker scheduling.
- `map_driver`: maps or unmaps a major to an endpoint and optional label.
- `do_mapdriver`: RS-only runtime driver mapping call.
- `dmap_unmap_by_endpt`: unmaps all majors owned by an endpoint.
- `map_service`: maps boot services with device-driver properties.
- `init_dmap`: initializes all entries and maps `CTTY_MAJOR` to VFS.
- `dmap_driver_match`, `get_dmap_by_major`, `get_dmap_by_endpt`: lookup helpers.
- `dmap_endpt_up`: handles restarted block/character drivers.

Important behavior:
- Unmapping a character driver invalidates filps for that major.
- RS-provided labels are copied from RS and resolved through DS.
- Mapped services are marked `FP_SRV_PROC`.
- Driver restart handling:
  - block drivers trigger `bdev_up`.
  - character drivers stop waiting workers and invalidate open filps.
- `CTTY_MAJOR` is special and handled by VFS itself.
