# File Research: sources/local-fs/jfsutils/libfs/open_by_label.c

This file locates and opens JFS filesystems or external journal devices by UUID or label. It supports regular block devices, EVMS, md RAID, `/proc/partitions`, and old LVM proc layouts.

Main functions:
- `open_check_label()` opens a candidate device read-only or read/write exclusive according to global `LogOpenMode`, reads either a log superblock or filesystem superblock, and compares UUID or label.
- `walk_dir()` recursively scans a directory tree for block devices, skipping `.`, `..`, and `.nodes`.
- `open_by_label()` tries `/proc/evms/volumes`, `/dev/evms`, `/proc/mdstat`, `/proc/partitions`, and `/proc/lvm/VGs/*/LVs` in that order, returning the first matching opened `FILE *`.

Integration points:
- `logredo.c` uses this to find external journals and active filesystems listed in a journal.
- `LogOpenMode` defaults to `O_RDWR | O_EXCL`, but logdump can set it to `O_RDONLY`.
- Uses `fopen_excl()` from `utilsubs.h`, superblock/logsuper endian swapping, and UUID comparisons.

Risks and notes:
- Several path buffers are fixed at 100 bytes and populated with `strcpy()`, `strcat()`, and `sprintf()`; deep or long device paths can overflow them.
- `uuid_t` is reused as a byte buffer for labels when `is_label` is true, with 16-byte `strncmp()` comparisons.
- The proc paths target older Linux storage stacks; modern systems may not expose EVMS or old LVM proc directories.
