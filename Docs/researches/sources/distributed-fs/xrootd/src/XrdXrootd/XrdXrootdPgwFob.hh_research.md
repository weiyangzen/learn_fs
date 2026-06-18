# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPgwFob.hh

## Purpose

`XrdXrootdPgwFob` tracks page-write checksum or recovery failures for one `XrdXrootdFile`. It records page offsets that are currently bad, counts total errors and later fixes, and gives page-write logic a bounded way to decide whether too many unresolved page errors have accumulated.

## Important APIs, types, and functions

The class exports `addOffs()`, `delOffs()`, `hasOffs()`, and `numOffs()`. Offsets are normalized by shifting the page offset by `XrdProto::kXR_pgPageBL`; short final-page writes encode `dlen` in the low bits so the same page number can distinguish full and partial page records. `badOffs` is a `std::set<kXR_int64>` protected by `fobMutex`.

## Control flow

Page-write code calls `addOffs()` when a page is detected as bad. The method inserts the encoded offset, increments `numErrs`, and returns whether unresolved bad offsets are still within `kXR_pgMaxEos`. A later successful correction calls `delOffs()`, increments `numFixd`, and erases the encoded offset. Readers can query one offset via `hasOffs()` or total unresolved/fixed/error counts through `numOffs()`.

## State and persistence behavior

All state is in-memory and scoped to the owning `XrdXrootdFile`; there is no durable persistence in this header. The destructor is out-of-line and is integrated with page-write support code. The mutex makes the set safe for concurrent page-write/error-recovery activity on the same file object.

## Dependencies and integration points

The type depends on `XProtocol.hh` for page geometry constants and `XrdSysPthread.hh` for locking. It is referenced from `XrdXrootdFile`, page-write control, and bad-checksum handling paths.

## Risks and edge cases

The offset encoding must stay consistent with protocol page constants; changing page size or bit layout without updating this class can collide entries. Duplicate bad offsets still increment `numErrs`, so the counter is an event count rather than the set cardinality. `addOffs()` only reports whether the set is below the protocol limit; callers must enforce the returned value.

## Test signals

Relevant tests should exercise full-page and short-page encoding, duplicate insertion, deletion of absent offsets, concurrent add/delete behavior, and caller behavior when `kXR_pgMaxEos` is exceeded. Integration signals come from page-write checksum and retry tests.
