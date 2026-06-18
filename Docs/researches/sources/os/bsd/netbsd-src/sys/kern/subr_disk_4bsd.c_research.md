# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_disk_4bsd.c

## Summary
Implements simple 4BSD-style `readdisklabel()` and `writedisklabel()` routines for ports using the basic scheme.

## Main Responsibilities
- Initializes minimal default disklabel geometry and raw partition fields before reading.
- Reads `LABELSECTOR` and scans for a valid `DISKMAGIC`/checksum disklabel.
- Writes an updated disklabel back over an existing valid on-disk label.

## Important Behavior
Read setup makes the raw partition cover `d_secperunit`, sets partition `a` to the whole raw partition as `FS_BSDFFS`, and scans the first sector at `sizeof(long)` alignment for a valid label.

Write chooses the requested partition unless that partition has nonzero offset, in which case it falls back to partition `a` if possible. It only overwrites an existing valid label and returns `ESRCH` if none is found.

## Dependencies
Uses `geteblk()`, driver strategy callbacks, `biowait()`, `brelse()`, disklabel checksum helpers, and disk partition macros.

## Risks
The writer does not create a new label if no valid label is already present. The implementation assumes the simple 4BSD sector placement model.
