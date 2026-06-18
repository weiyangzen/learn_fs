# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi.c

## Purpose

`ddi.c` implements kernel functions required by the UNIX Device Driver Interface and STREAMS compatibility interfaces. Many routines are function equivalents of macros or legacy DDI/SVR4 APIs, made available as callable kernel symbols for drivers.

The file covers device number manipulation, driver parameters, buffer headers, time conversions, STREAMS queue/perimeter helpers, queue callback wrappers, device association, and kernel virtual address translation.

## Device Number Helpers

The file provides major/minor extraction and construction:

- `getmajor`, `getemajor`
- `getminor`, `geteminor`
- `etoimajor`, `itoemajor`
- `makedevice`
- `cmpdev`, `expdev`

The implementation handles `_LP64` and non-`_LP64` layouts with `NBITSMINOR64`/`MAXMIN64` versus `NBITSMINOR`/`MAXMIN`. illumos has a direct internal/external major mapping, so `itoemajor()` mostly validates and returns the same major.

## Basic DDI Utilities

`drv_getparm()` returns selected kernel parameters such as current process, process group, lbolt, time, PID, session ID, and credentials. It uses process locks where needed.

`drv_setparm()` increments CPU system statistics for receive, transmit, modem, raw character, canonical character, and output character counters.

`getrbuf()` allocates and initializes a `struct buf`; `freerbuf()` finalizes and frees it.

`btop()`, `btopr()`, and `ptob()` convert between byte counts and page counts.

`drv_hztousec()` and `drv_usectohz()` convert between ticks and microseconds, clamping tick-to-usec overflow to `LONG_MAX`.

`time_to_wait()` computes an absolute lbolt timeout target for timed condition-variable waits.

## STREAMS Macro Wrappers

The file exposes function versions of STREAMS helpers:

- `datamsg()`
- `OTHERQ()`
- `RD()`
- `WR()`
- `SAMESTR()`

`bcanputnext()` and `canputnext()` check downstream flow control. `canputnext()` uses stream reference locking, detects a full downstream service queue, sets `QWANTW` when blocked, and handles the common non-full path cheaply.

## Queue Lifecycle

`qprocson()` inserts a driver/module queue into the stream so put and service routines can run. It avoids reinsertion on reopen unless `_QINSERTING` is set.

`qprocsoff()` disables service/put processing, removes the queue, and is idempotent for `QWCLOSE`.

`freezestr()` freezes an entire stream by blocking entry and taking queue locks across the stream. `unfreezestr()` releases queue locks, unblocks the stream, and releases the stream reference. This is explicitly special because it acquires multiple queue locks.

## STREAMS Waiting And Perimeters

`qwait_sig()` and `qwait()` are used by open/close procedures to sleep while temporarily lowering perimeter exclusion. They:

- Exit the outer perimeter if present.
- Drop inner exclusive state and syncq count under lock.
- Broadcast waiters when needed.
- Drain queued syncq work when possible.
- Otherwise wait on `sq_exitwait`.
- Re-enter the syncq before returning.

`qwait_sig()` returns whether a signal interrupted the wait. `qwait()` waits uninterruptibly.

`qwait_rw()` is a consolidation-private variant for synchronous read/write entry points. It drops exclusive put access, waits for exit activity, then re-enters as `SQ_PUT`, returning whether a signal was seen.

`qwriter()` dispatches asynchronous upgrade to exclusive access at either the inner or outer perimeter through `qwriter_inner()` or `qwriter_outer()`.

## Queue Callbacks

`qtimeout()` and `qbufcall()` schedule callbacks that enter the queue’s inner perimeter via `qcallbwrapper`. They allocate `callbparams_t` under the syncq lock, store cancel metadata, schedule `timeout()` or `bufcall()`, and record the callback ID.

`quntimeout()` and `qunbufcall()` cancel those callbacks. They serialize cancellation through `sq_callbflags`, set the cancel ID/type, wake blocked callback wrappers, perform the underlying cancel operation, free callback parameters as appropriate, clear cancellation state, and wake waiters.

## Queue Device Association

`qassociate()` associates a stream with a specific hardware instance. Passing `-1` clears association. Otherwise it gets the stream vnode’s major number, holds the devinfo for the requested instance without attaching it, associates the queue with that devinfo, and releases the hold.

The comments explain the contract: `qassociate()` cannot drive blocking attach from a STREAMS put context, so callers must handle failure if the requested instance is detached or inaccessible.

## Address Translation

`kvtoppid()` returns the physical page frame number for a kernel virtual address through `hat_getpfnum(kas.a_hat, addr)`. It is the SVR4MP-style replacement for older platform-specific `hat_getkpfnum()` interfaces.

## Dependencies

This file depends heavily on:

- Device number layout macros.
- Process/session/credential state.
- CPU statistics.
- Buffer cache initialization.
- STREAMS internals: queues, streams, syncqs, perimeters, callback parameter lists.
- Timeout and bufcall machinery.
- Devinfo association helpers and vnode device numbers.
- HAT/kernel address-space APIs.

## Research Notes

`ddi.c` is glue code, but much of it sits on sensitive STREAMS synchronization boundaries. Important audit areas are `canputnext()` stream reference handling, `freezestr()` multi-lock ordering, `qwait*()` perimeter exit/reentry semantics, callback cancellation races in `quntimeout()`/`qunbufcall()`, and `qassociate()` failure handling in drivers that call it from nonblocking contexts.
