# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiShMam.cc

## Purpose
`XrdSsiShMam.cc` implements the default shared-memory map backend for `XrdSsiShMat`. It stores fixed-size typed values keyed by strings in a memory-mapped file, supports atomic publication by creating `.new` files and renaming them into place, and provides add/delete/get/enumerate/resize/sync operations.

## Important APIs and Functions
The public implementation covers `AddItem`, `Attach`, `Create`, `DelItem`, `Detach`, two `Enumerate` forms, `Export`, `GetItem`, `Info`, `Resize`, and three `Sync` forms. Internal helpers include `ExportIt`, `Find`, `Flush`, `HashVal`, `Lock`, `NewItem`, `ReMap`, `RetItem`, `SetLocking`, `Snooze`, `SwapMap`, `UnLock`, and `Updated`. The private on-disk header is `ShmInfo`.

## Control Flow
`Create` validates parameters, calculates header/index/item layout, creates `<path>.new`, sizes and maps it, initializes `ShmInfo`, and keeps relaxed locking until export. `Export` flushes if needed, optionally locks the previous file, renames the new file over the visible path, bumps the old version number to notify existing mappings, and resets locking. `Attach` waits for the file, locks it, maps it, validates type/implementation/hash compatibility, and checks inode stability. `AddItem`/`DelItem`/`GetItem` remap when version changes, optionally flock, find hash-chain entries, and update counts/free lists.

## State and Persistence
The map persists in a backing file whose first bytes are `ShmInfo`, followed by item storage and an index table. Runtime state tracks fd, mapping base/size, temp path, index pointer, slot/item/key sizing, locks, access mode, reuse/multiple-writer flags, version, timeout, and sync queue counters.

## Dependencies and Integration Points
The file depends on POSIX file, flock, mmap, rename, stat, pread/pwrite, zlib `crc32`, SSI atomics, `XrdSsiShMat`, and `XrdSysE2T`. It is constructed by `XrdSsiShMat::New` and wrapped by the templated `XrdSsi::ShMap<T>` API.

## Risks and Test Signals
Risks include crash consistency around rename/version bump, stale mappings during resize/export, `Info` buffer length off-by-one checks, reuse/free-list races, `Flush` returning the inverse of the local `rc` expectation, and sync queue size zero causing immediate flush checks. Tests should cover create/export/attach compatibility, add duplicate with and without replace, delete with/without returned value, reuse on/off, multiple writer locking, enumerate while updating, resize preserving keys, version-triggered remap, timeout waiting, permission validation, and sync mode changes.
