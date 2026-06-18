# sources/test-tools/fio/debug.h

Purpose: Defines fio debug categories, warning-once helpers, and the `dprint()` interface.

Important APIs/types: The debug enum spans categories such as file, io, diskutil, job, time, network, zbd, and `FD_DEBUG_MAX`. Externs include `fio_debug_jobno`, `fio_debug_jobp`, and `fio_warned`. `fio_did_warn()` sets warning bits. Warning masks include root flush, verify buffer, zoned bug, iolog drop, fadvise, and btrace zero. In debug builds it declares `struct debug_level`, `debug_levels`, `fio_debug`, `__dprint()`, and a filtering macro; otherwise `dprint()` is an empty inline.

Control flow: Runtime code calls `dprint(category, ...)`; debug builds test `fio_debug` and forward to logging, while normal builds discard the call.

State/persistence: Warning bits are global through `fio_warned`; debug mask/job selection are global. `fio_did_warn()` mutates the shared warning mask.

Dependencies/integration: Includes fio boolean types and is widely included across the codebase.

Risks: `fio_did_warn()` assumes `fio_warned` is initialized. Warning bit allocation is manual and can collide if extended carelessly. Non-debug builds still type-check only the inline signature, not format strings.

Test signals: Unit or integration tests should verify warning-once behavior and debug category filtering with `FIO_INC_DEBUG`.
