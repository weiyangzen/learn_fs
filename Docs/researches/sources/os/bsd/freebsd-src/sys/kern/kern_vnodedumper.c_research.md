# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_vnodedumper.c

## Purpose
Provides a vnode-backed dumper for live kernel minidumps, allowing privileged callers to write a live dump to an open file.

## Key Interfaces
- `livedump_start()` validates an fd, privilege, flags, and write access, then starts a live dump to the vnode.
- `livedump_start_vnode()` builds a temporary `dumperinfo`, serializes live dumps, locks the vnode/range, and invokes `minidumpsys()`.
- `vnode_dumper_start()` initializes dumper offset state and rejects encryption keys.
- `vnode_dump()` writes dump chunks to the vnode.
- `vnode_write_headers()` writes the kernel dump header at the adjusted end offset.

## State And Locking
A global `livedump_sx` permits only one live dump at a time. During a dump, the target vnode's full range is write-locked with `vn_rangelock_wlock()` and the vnode is exclusively locked. The temporary dumper stores the target vnode in `di->priv`.

## Control Flow
When `MINIDUMP_PAGE_TRACKING` is enabled, `livedump_start()` checks `PRIV_KMEM_READ`, rejects nonzero flags, obtains a writable vnode from the file descriptor, and calls `livedump_start_vnode()`. The vnode path creates a dumper with the requested compression, takes the live-dump sx lock, stores the vnode, locks the file range and vnode, invokes start/finish eventhandlers, quiets sanitizer reporting around `dump_savectx()` and `minidumpsys(livedi, true)`, then unlocks and destroys the dumper. Dump callbacks write memory chunks with `vn_rdwr(..., IO_NODELOCKED, ...)`; a null virtual address marks completion.

## Integration Notes
Depends on kernel dump infrastructure, minidump page tracking, vnode/file descriptor capability checks, eventhandlers (`livedumper_start`, `livedumper_dump`, `livedumper_finish`), compression settings, and machine context save code.

## Risks
The feature is compiled out with `EOPNOTSUPP` unless `MINIDUMP_PAGE_TRACKING == 1`. Dump writes occur while holding the vnode lock and full-range lock, so filesystem behavior and blocking characteristics matter. Encryption is explicitly unsupported for livedumps. Eventhandlers can veto or fail dump progress by setting errors.
