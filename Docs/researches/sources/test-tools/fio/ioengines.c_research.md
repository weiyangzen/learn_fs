# sources/test-tools/fio/ioengines.c

## Purpose
Implements fio's I/O engine registry, dynamic engine loading, engine lifecycle cleanup, and wrapper functions that mediate between core `io_u` scheduling and engine callback implementations.

## Important APIs, Types, and Functions
Public functions include `register_ioengine`, `unregister_ioengine`, `load_ioengine`, `free_ioengine`, `close_ioengine`, `td_io_prep`, `td_io_getevents`, `td_io_queue`, `td_io_init`, `td_io_commit`, `td_io_open_file`, `td_io_close_file`, `td_io_unlink_file`, `td_io_get_file_size`, and `fio_show_ioengine_help`. Internal helpers include `check_engine_ops`, `find_ioengine`, dynamic `dlopen_*` helpers, `async_ioengine_sync_trim`, and `async_ioengine_sync_syncfs`.

## Control Flow
Static engines register on the global `engine_list`; dynamic engines are loaded with `dlopen()` and resolved by engine symbol or `get_ioengine()`. `load_ioengine()` resolves aliases such as `aio`/`linuxaio` to `libaio`, validates operation table version and required callbacks, and returns ops to initialization. Queueing marks an `io_u` in flight, logs it, updates issue counters, calls engine `queue`, handles ZBD callbacks, backs out counters on busy, optionally commits async batches, records issue time, and updates depth/completion maps. Completion wrappers call engine `commit`, `getevents`, and `event`. File wrappers handle open/close accounting, invalidation, fadvise, write hints, direct I/O setup, unlink, and size queries.

## State and Persistence Behavior
Global engine state is the `engine_list` and dynamic library handles stored in `ioengine_ops`. Per-thread state includes `td->io_ops`, engine options `td->eo`, open file counts, in-flight/queued counts, and file flags. Persistent effects are engine-driven I/O and file open/unlink operations.

## Dependencies and Integration Points
Depends on `fio.h`, diskutil, ZBD support, dynamic linker APIs, file locking, file logging, fadvise/write hints, and every engine's `struct ioengine_ops` contract. `init.c` loads engines and engine options, while `io_u.c` calls the wrapper APIs.

## Risks
Engine ABI compatibility hinges on `FIO_IOOPS_VERSION`. Dynamic loading has several symbol naming paths and must close handles correctly. `td_io_queue()` updates counters before calling the engine and must exactly reverse them on `FIO_Q_BUSY`. Offload overlap unlock ordering is subtle. File open error paths must balance disk-util counters, file refs, and engine close callbacks. `td_io_open_file()` sets `FIO_RAWIO` by mutating engine flags for direct I/O, which can matter if ops are shared.

## Test Signals
Useful signals include static and dynamic engine loading tests, `--enghelp`, sync and async engine jobs, busy queue injection, direct-I/O alignment failures, fadvise/write-hint jobs, openfiles limit tests, ZBD jobs, and sanitizer runs around engine load/unload.
