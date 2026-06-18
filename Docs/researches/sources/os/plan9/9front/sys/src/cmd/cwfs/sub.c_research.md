# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/sub.c

Purpose: Large shared utility layer for cwfs. It handles filesystem lookup helpers, fid/path management, permissions, file locks, free-list allocation, message queues, device dispatch, reaming/recovery/init routing, formatting, and byte swapping.

Important behavior:
- Filesystem/fid helpers: `fsstr()`, `dev2fs()`, `fs_chaninit()`, `fileinit()`, `filep()`, `newfp()`, `freefp()`.
- Access control: `iaccess()` checks owner/group/other bits, special uid/group behavior, `duallow`, and privileged console/allowed user access. `isallowed()` gates console or configured allowed uid.
- Temporary locks: `tlocked()` manages `Tlock` entries with expiration.
- Path allocation: `newwp()` and `freewp()` manage fixed `Wpath` pool refs.
- Allocation/freeing: `bufalloc()`, `buffree()`, `truncfree()`, and `addfree()` manage superblock free lists and recursive indirect block freeing.
- Formatting: `%Z` prints device config syntax, `%G` prints tags, `%T` installed elsewhere for times.
- Reaming: `rootream()` creates the root directory block; `superream()` initializes super/free metadata.
- Message buffers: `mbinit()`, `mballoc()`, `mbfree()` manage large/small preallocated message buffers and readahead buffers.
- Queues: `newqueue()`, `fs_send()`, `fs_recv()` implement semaphore-backed circular queues.
- Device dispatch: `devread()`, `devwrite()`, and `devsize()` route by `Device.type`.
- Device setup: `devream()`, `devrecover()`, and `devinit()` recursively initialize or format device trees.
- Byte swapping: `swab2()`, `swab4()`, `swab8()`, and `swab()` convert on-disk block types between native and foreign endianness.

Notable details:
- `devwrite()` returns success immediately when global `readonly` is set, preventing actual writes.
- `sdof()` converts device config to `/dev/sdXY` names.
- `superaddr()` and `getraddr()` defer to cw-specific root/superblock addresses for cached-WORM devices.
- `swab()` understands all disk tags except data-like byte arrays, which are intentionally left unchanged.
