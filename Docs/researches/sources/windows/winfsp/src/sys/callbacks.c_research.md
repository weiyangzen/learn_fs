# File Research: sources/windows/winfsp/src/sys/callbacks.c

Kernel driver Fast I/O and cache-manager resource callback implementation.

Fast I/O:
- `FspFastIoCheckIfPossible()` currently asserts and returns `FALSE`, disabling this fast path.

Section/cache callbacks:
- `FspAcquireFileForNtCreateSection()` acquires the file node full lock exclusively and marks TLS `CreateSection`.
- `FspReleaseFileForNtCreateSection()` clears the flag and releases.
- `FspAcquireForModWrite()` tries full exclusive acquisition for mapped page writer and returns paging resource to release; returns `STATUS_CANT_WAIT` if it cannot acquire without waiting.
- `FspReleaseForModWrite()` temporarily restores top-level IRP to `FSRTL_MOD_WRITE_TOP_LEVEL_IRP` before release to tolerate observed external corruption.
- `FspAcquireForCcFlush()` handles both synthetic top-level values and real IRP top levels, preserving/restoring top flags around full acquisition.
- `FspReleaseForCcFlush()` reverses that state.

Lazy writer and read-ahead:
- `FspAcquireForLazyWrite()` exclusive-acquires full lock, records lazy-write thread, and sets top-level IRP to cache top-level.
- `FspReleaseFromLazyWrite()` validates thread/top-level state, clears it, releases.
- `FspAcquireForReadAhead()` shared-acquires full lock and sets cache top-level.
- `FspReleaseFromReadAhead()` clears top-level and releases.

Top-level propagation:
- `FspPropagateTopFlags()` propagates acquisition/top flags from top-level IRP context into nested IRPs when recursion is detected on the same file node.

Primary role:
- Coordinates WinFsp file-node resource ownership with Windows cache manager, memory manager, oplock, and recursive I/O expectations.
