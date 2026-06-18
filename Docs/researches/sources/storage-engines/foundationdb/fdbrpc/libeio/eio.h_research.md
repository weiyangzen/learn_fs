# sources/storage-engines/foundationdb/fdbrpc/libeio/eio.h

## Purpose

`eio.h` is the public API contract for the bundled libeio asynchronous I/O library. It defines request types, callback signatures, request layout, result macros, tuning APIs, wrapper constructors, groups, and cancellation/submission functions.

## Important APIs, types, and functions

Key types are `eio_req`, `eio_dirent`, `eio_cb`, `eio_wd`, `eio_uid_t`, `eio_gid_t`, `eio_ssize_t`, `eio_ino_t`, and `eio_tstamp`. Important enums cover readdir flags, directory entry types, memory sync/touch flags, sync-file-range flags, fallocate flags, request types from `EIO_CUSTOM` through `EIO_READLINK`, mlockall constants, and priorities. `struct eio_req` stores path/FD parameters, buffers, offsets, result/error state, cancellation flag, priority, user data, finish/destroy/feed callbacks, and group links. Public functions include initialization/polling/tuning/counters, many operation wrappers, group APIs, `eio_submit()`, `eio_cancel()`, and `eio_sendfile_sync()`.

## Control flow, state, and persistence

This header declares the lifecycle contract: callers create a zeroed request through wrappers or manually, submit it, wait for `want_poll` notification, call `eio_poll()` regularly, inspect `result`/`errorno` in the finish callback, and let libeio destroy request-owned resources. Runtime state lives in `eio.c` and in active `eio_req` objects. Nothing is persisted across process exit.

## Dependencies and integration points

It includes `stddef.h`, `signal.h`, `sys/types.h`, and `stdio.h`. `AsyncFileEIO.h` includes this header and uses both wrappers and direct manual `eio_req` construction for Apple `F_FULLFSYNC` custom handling. CMake adds `fdbrpc/libeio` as a private include directory for `fdbrpc` and `fdbrpc_sampling`.

## Risks and test signals

The struct is part of the in-repo C/C++ ABI between `AsyncFileEIO` and `eio.c`; field changes can break manual request construction. `cancelled` is `unsigned char` on i386/amd64 and `sig_atomic_t` elsewhere, so memory-order assumptions are minimal. Request buffers may be owned either by the caller or by libeio depending on flags, which is an easy source of lifetime bugs. Test by building `AsyncFileEIO`, exercising direct and wrapper-created requests, and checking finish callbacks do not access freed data.
