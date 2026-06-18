# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsCPFile.hh

## Purpose

`XrdOfsCPFile.hh` declares `XrdOfsCPFile`, the low-level checkpoint-file abstraction that owns a checkpoint filename/file descriptor and exposes create, append, reserve, restore-info, sync, target lookup, deletion, and error-state operations.

## Important APIs, Types, and Functions

- `Append(const char *data, off_t offset, int dlen)` records original bytes for a source-file offset. Callers are expected to call `Sync()` after appends.
- `Create(const char *lfn, struct stat &Stat)` creates a checkpoint bound to a source LFN and original stat metadata.
- `Destroy()` removes the checkpoint; `ErrState()` marks it as a failed checkpoint.
- `FName(bool trim=false)` returns the checkpoint path or basename.
- `isActive()` reports whether a checkpoint filename is established.
- `Reserve(int dlen, int nseg)` preallocates space for data and segment records.
- Nested `rInfo` carries restore output: `srcLFN`, original `fSize`, original `mTime`, `DataVec`, `DataNum`, `DataLen`, and private backing buffer.
- `RestoreInfo(rInfo&, const char *&ewhy)` validates and extracts all restore data from the checkpoint.
- Static `Target(const char *ckpfn)` returns a heap-allocated source filename or explanatory text for a checkpoint path.
- Private static helpers generate checkpoint paths and recover source LFN from xattrs.

## Control Flow and Contracts

The class separates checkpoint lifecycle into explicit phases: `Create()` establishes the file and header; `Reserve()` prepares for upcoming mutations; `Append()` records original data; `Sync()` commits; `RestoreInfo()` reads a checkpoint after a crash or explicit restore; `Destroy()` or `ErrState()` ends lifecycle. Constructors can also bind to a preexisting checkpoint filename, which is used by startup recovery.

Return values are mostly `0` or negative errno. Callers must treat `rInfo`'s pointers as owned by the `rInfo` instance and avoid using them after destruction.

## State and Persistence Behavior

`ckpFN` is heap-owned and identifies the persistent checkpoint. `ckpFD` is held open during creation/append. `ckpDLen` and `ckpSize` track logical checkpoint bytes for quota/reservation. The persistent format and validation are implemented in the `.cc` file; this header defines the stable restore contract.

## Dependencies and Integration Points

The header depends only on standard integer/time types and forward declarations for `stat` and `XrdOucIOVec`, keeping it usable by checkpoint management code without pulling in OSS internals. `XrdOfsChkPnt.hh` includes it directly and composes an `XrdOfsCPFile`.

## Risks and Edge Cases

- `Target()` returns allocated memory; every caller must free it.
- `isActive()` is filename-based, not fd-based. A preexisting recovery object is active before opening the file.
- `FName()` returns a static literal `"???"` when inactive, so callers must not free its result.
- The public comments use `off_t` and `struct stat` but the header only includes `<ctime>`/`<cstdint>`; inclusion order must supply `off_t` through platform headers in consumers.

## Test Signals

Header-level tests are mostly integration tests: instantiate active and inactive objects, verify `rInfo` destructor frees restore buffers without leaks, compile consumers that include only this header plus needed system headers, and validate return-value conventions through the implementation tests.
