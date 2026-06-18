# File Research: sources/virtualization/libblockdev/src/plugins/fs/exfat.c

## Role

`exfat.c` implements filesystem-plugin operations for exFAT filesystems through the exfatprogs command-line tools.

## Dependency Model

The module caches runtime dependency checks for:

- `mkfs.exfat`
- `fsck.exfat`
- `tune.exfat`

`bd_fs_exfat_is_tech_avail()` rejects resize mode because exFAT resizing is unsupported, then maps modes to utilities:

- mkfs: `mkfs.exfat`
- check/repair: `fsck.exfat`
- set-label/query/set-uuid: `tune.exfat`
- wipe/resize: no dependency, but resize is rejected up front

The dependency array contains four entries, with `tune.exfat` duplicated for the fourth slot.

## Info Object

`BDFSExfatInfo` contains label, UUID, sector size, sector count, and cluster count.

Copy/free helpers duplicate label and UUID and copy numeric fields.

## mkfs Options and Creation

`bd_fs_exfat_mkfs_options()` maps generic options:

- label -> `-n`
- extra args appended
- `no_pt` may add `-P none`, but only when `mkfs.exfat` is detected as exfatprogs 1.4.0 or newer

`bd_fs_exfat_mkfs()` runs `mkfs.exfat <device>` with extra arguments.

## Check and Repair

`bd_fs_exfat_check()` runs `fsck.exfat -n <device>`. If the command fails with exit status 1, the code clears the error but still returns the command result.

`bd_fs_exfat_repair()` runs `fsck.exfat -y <device>`. If the command fails with exit status 1, it clears the error and returns success, treating "corrected" status as non-fatal.

## Label Handling

`bd_fs_exfat_set_label()` runs `tune.exfat -L <label> <device>`.

`bd_fs_exfat_check_label()` validates that the label is valid UTF-8 and can be converted to UTF-16LE, then enforces a maximum encoded size of 22 bytes.

## UUID Handling

`bd_fs_exfat_set_uuid()` runs `tune.exfat -I <id> <device>`. If no UUID is supplied, it generates a random 32-bit value and formats it as `0x%08x`.

Supplied UUIDs are accepted in:
- `0x...` form
- udev-like `XXXX-XXXX` form, converted to `0xXXXXXXXX`
- raw hex form, prefixed with `0x`

`bd_fs_exfat_check_uuid()` accepts `NULL`, strips the dash from `XXXX-XXXX`, parses hexadecimal, and requires the value to fit in 32 bits.

## Query

`bd_fs_exfat_get_info()` first uses common blkid probing to fill UUID and label. It then runs `tune.exfat -v <device>`, splits output by line, and parses values from lines containing:

- `Block sector size`
- `Number of the sectors`
- `Number of the clusters`

It fails if any of these numeric values remain zero.

## Notable Risks

- exFAT info parsing depends on `tune.exfat -v` output text.
- Generated UUIDs use GLib random integers and are only 32-bit exFAT volume IDs.
- Label length is checked after UTF-16LE conversion, which matches exFAT label storage better than byte-counting UTF-8.
- `DEPS_LAST` is 4 while only three unique tools are used; the duplicate `tune.exfat` entry appears intentional or harmless but should be kept in sync with masks if edited.
