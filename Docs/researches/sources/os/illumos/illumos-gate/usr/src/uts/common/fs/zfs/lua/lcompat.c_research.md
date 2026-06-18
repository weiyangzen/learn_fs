# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lcompat.c

## Role

`lcompat.c` provides illumos/ZFS compatibility helpers used by the embedded Lua runtime where standard libc behavior or numeric operations need local substitutes.

## Main Responsibilities

- Implements `lcompat_sprintf` as a bounded `vsnprintf` wrapper returning `ssize_t`.
- Implements `lcompat_strtoll` with whitespace skipping, optional sign, base-10/base-8/base-16 prefix handling, digit scanning, and end-pointer reporting.
- Implements integer exponentiation by squaring in `lcompat_pow`, returning zero for negative exponents.
- Implements `lcompat_hashnum`, a deterministic integer hash mixer for numeric table keys.

## Integration Points

`llimits.h` routes numeric hashing through `lcompat_hashnum` when building table code. `lobject.c` uses `lcompat_sprintf` for `%p` formatting in Lua error/string helpers.

## Risk Notes

These helpers intentionally implement a small subset of libc-like behavior. Overflow is not checked in `lcompat_strtoll` or `lcompat_pow`; callers rely on Lua's surrounding numeric semantics.
