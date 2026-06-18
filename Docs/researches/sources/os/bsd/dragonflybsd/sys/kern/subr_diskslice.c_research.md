# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_diskslice.c

## Summary
Implements DragonFly BSD cooked disk-slice support: validating I/O against slices and disklabel partitions, translating logical offsets to media offsets, serving disklabel/slice ioctls, and managing in-core `struct diskslices` lifecycle.

## Main Responsibilities
- `dscheck()` validates `bio_offset` and transfer size against the requested slice/partition, protects reserved label areas, clips EOF reads, and returns a pushed BIO with translated media offset.
- `dsioctl()` handles disklabel, media-size, sector-size, partition-info, slice-info, sync/reprobe, and write-label ioctls.
- `dsmakeslicestruct()`, `dsgone()`, `free_ds_label()`, and `set_ds_label()` allocate, free, and update in-core slice/disklabel state.
- `dsopen()`, `dsclose()`, `dsisopen()`, and `dssize()` track open partitions and trigger disk or slice reprobes when label areas were written.

## Important Behavior
Whole-disk raw access is special: labels are not interpreted for `WHOLE_DISK_SLICE`, normal partition numbers below 128 are rejected, and higher partition numbers can be encoded into the high byte of the BIO offset for raw pass-through. For normal slices, partition bounds come from the loaded disklabel ops. Label writes set `DSF_REPROBE`, and close/ioctl paths send synchronous disk management messages followed by `devfs_config()`.

## Risks
Callers must reload disk/slice pointers after `dsclose()` or ioctls that reprobe because `ssp` and `sp` may be invalidated. Offset translation assumes sector alignment and power-of-two sector size at key points. Reserved-area writes require `ds_wlabel`; otherwise they fail with `EROFS`. Accessing a partition before its disklabel is loaded or present returns errors.
