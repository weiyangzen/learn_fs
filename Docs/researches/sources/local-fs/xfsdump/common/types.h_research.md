# File Research: sources/local-fs/xfsdump/common/types.h

## Role

This header defines common project-wide scalar types, limits, booleans, return codes, and miscellaneous compatibility typedefs.

## Types And Macros

It includes standard integer types, defines member-size/offset helpers, fixed page-size constants, aliases such as `size32_t`, `size64_t`, `time32_t`, `xfs_ino_t`, `ix_t`, and `bool_t`.

It also provides `constpp` for `getsubopt()` token arrays.

## Limits

The `MKMAX`, `MKSMAX`, and `MKUMAX` macros derive signed/unsigned maximums for many project types, including 32-bit, 64-bit, size, offset, inode, time, and index types.

## Booleans

Boolean values are integer constants:

- true
- false
- unknown
- error

## Return Codes

`rv_t` enumerates internal result reasons used across dump/restore and by `mlog` final summaries. Values cover success, media conditions, EOD/EOF/EOM, resource errors, interruption, corruption, quit, drive timeout/media/protection problems, core, option/init/permission/compatibility errors, incomplete runs, inventory errors, usage-only, already-exists, none, and unknown.

## Compatibility Typedefs

The header aliases system/XFS structures such as `stat_t`, `stat64_t`, `getbmapx_t`, and `fsdmidata_t`.

## Preemption Flags

Defines `PREEMPT_FULL` and `PREEMPT_PROGRESSONLY` for cooperative preemption/progress checks.
