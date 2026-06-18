# sources/user-network-fs/samba/source3/modules/vfs_cacheprime.c

## Purpose
`vfs_cacheprime.c` is a performance-oriented Samba VFS module that primes the kernel buffer cache before file reads or `sendfile()` transfers. It performs large sequential `pread()` calls, intended to match RAID stripe widths, so later zero-copy or ordinary reads have lower latency.

## Important APIs, types, and functions
- `READAHEAD_MIN` and `READAHEAD_MAX` clamp configured read-ahead size between 128 KiB and 100 MiB.
- Global `g_readsz` and `g_readbuf` hold the process-wide read-ahead buffer and size.
- `prime_cache()` stores per-file-handle progress in a VFS fsp extension of type `off_t`, reads from the file with `sys_pread()`, and disables further read-ahead for that handle on read failure by setting `*last = -1`.
- `cprime_connect()` reads `cacheprime:debug` and `cacheprime:rsize`, allocates the global buffer once, and then delegates connect.
- `cprime_sendfile()` primes only when `offset == 0`, then delegates `SMB_VFS_NEXT_SENDFILE()`.
- `cprime_pread()` primes before all delegated preads when the global buffer exists.
- `vfs_cacheprime_init()` registers the module as `cacheprime`.

## Control flow
On the first successful connect in an smbd process, the module parses `cacheprime:rsize`, clamps it, and allocates one global buffer. Later connects in the same process do not reallocate or resize the buffer, even if share configuration differs, to avoid corrupting concurrent users. During reads, `prime_cache()` creates or fetches a per-fsp offset marker. If the current cached range already covers the requested offset/count, it skips work. Otherwise it reads `g_readsz` bytes starting at the last primed offset, advances the marker by the number of bytes actually read, and lets the original VFS operation proceed.

## State and persistence behavior
State is entirely in-process and non-persistent. `g_readbuf` and `g_readsz` are shared by all connections handled by the process. Each open file handle has its own fsp extension tracking the last primed offset or `-1` to suppress future attempts after an error. The module never changes file contents.

## Dependencies and integration points
The module depends on Samba VFS fsp extensions, loadparm module parameters, `sys_pread()`, and delegated `sendfile`/`pread` VFS operations. It is registered in `source3/modules/wscript_build` as `vfs_cacheprime` and is configured with `cacheprime:rsize` and `cacheprime:debug`.

## Risks and edge cases
- The global buffer is process-wide, so different shares in the same process cannot safely use different read-ahead sizes after the first allocation.
- `prime_cache()` uses `VFS_ADD_FSP_EXTENSION()` as though it returns a usable initialized `off_t`; the initial marker value depends on Samba extension allocation semantics.
- Large configured sizes can allocate up to 100 MiB per smbd process.
- On systems where `pread` is emulated with seek/read/seek, the module can be counterproductive, as the source comment warns.
- The module can perform extra I/O for workloads that do not benefit from sequential readahead.

## Test signals
No direct automated tests were found. Validation should compare read/sendfile latency and backend disk I/O with and without the module, test min/max `cacheprime:rsize` clamping, verify no repeated priming for already covered ranges, and confirm read errors disable further priming per file handle. Build registration in `wscript_build` is the static integration signal.
