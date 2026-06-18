# File Research: sources/os/linux/linux-stable/fs/pstore/Makefile

## Summary
Build rules for the pstore subsystem and its optional backends/frontends.

## Main Responsibilities
- Build `pstore.o` from `inode.o` and `platform.o` when `CONFIG_PSTORE` is enabled.
- Add `ftrace.o` and `pmsg.o` to `pstore.o` when their frontends are enabled.
- Build `ramoops.o` from `ram.o` and `ram_core.o`.
- Build `pstore_zone.o` from `zone.o`.
- Build `pstore_blk.o` from `blk.o`.

## Cross-File Interactions
The Makefile mirrors Kconfig feature boundaries: `platform.c` and `inode.c` are core; `ram.c`/`ram_core.c` are the RAM backend; `zone.c` is the zone manager; `blk.c` is the block-device backend.
