# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsHandle.cc

## Purpose

This file implements OFS shared file-handle tracking. It deduplicates active OSS file handles by path and access mode, manages reference counts and per-handle locking, tracks POSC ownership metadata, supports delayed retirement callbacks, and provides suppressed-error wrappers for handles that must remain readable/closable after write-side failure.

## Important APIs, types, and functions

`XrdOfsHandle::Alloc()` has path-based and dummy-handle variants. `Hide()` makes existing handles unfindable by clearing key length. `Activate()` attaches a real `XrdOssDF`. `Retire()` decrements references, removes table entries, closes/deletes OSS handles, and recycles handle objects. `Retire(XrdOfsHanCB*, int)` defers retirement through an expiry thread. `PoscSet()`, `PoscGet()`, and `PoscUsr()` manage persist-on-successful-close owner state. `Suppress()` wraps the OSS handle with `XrdOfsHanOssErr`.

Supporting classes include `XrdOfsHanTab` for hash tables, `XrdOfsHanKey` for CRC32 path keys, `XrdOfsHanPsc` for POSC metadata, `XrdOfsHanXpr` for deferred retire scheduling, and dummy/error OSS classes.

## Control flow

Path allocation locks the global table, finds an existing read-only or read-write entry, increments `Links`, releases the global lock, then tries to lock the handle. If it cannot lock quickly, it rolls back the link and returns a client delay. New handles are allocated in blocks, initialized, locked, added to the table, and counted in stats.

Retire requires the handle lock on entry. If reference count reaches one, it removes the handle from the appropriate table, recycles POSC data, frees path memory, swaps in the dummy OSS object, unlocks, and closes/deletes the real OSS handle outside the global lock. Deferred retire starts a background thread, schedules an `XrdOfsHanXpr`, and later calls the callback only if the handle is still uniquely referenced and active.

## State and persistence behavior

State is in memory: static global mutex, read-only and read-write hash tables, dummy OSS object, free handle list, POSC free list, expiry queue, and counters in `OfsStats`. POSC metadata includes queue offset and creator identity but durable queue persistence is handled by `XrdOfsPoscq`, not here.

## Dependencies and integration points

It depends on `XrdOssDF`, `XrdOfsStats`, `XrdSysMutex`, `XrdSysCondVar`, timers, and POSIX time. OFS file open/close paths use handles to share OSS file descriptors and coordinate POSC cleanup. `XrdOfsHanCB` lets higher-level code receive retirement callbacks.

## Risks and test signals

The global lock, per-handle lock, and expiry condition-variable lock interact in subtle ways. Tests should stress concurrent allocate/retire, lock timeout rollback, hash expansion, hidden handles, deferred retire rescheduling, and close error propagation. `PoscSet()` admits same creator reconnects but rejects different users unless re-enabled; recovery tests should pin that behavior. The dummy/error OSS wrappers intentionally return configured errors and must still allow close/stat/read paths required by callers.
