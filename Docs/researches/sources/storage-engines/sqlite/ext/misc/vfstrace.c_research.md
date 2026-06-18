# Research: sources/storage-engines/sqlite/ext/misc/vfstrace.c

## Purpose

`vfstrace.c` implements a configurable SQLite VFS shim that prints strace-like diagnostics for VFS and file I/O calls. Unlike `vfslog.c`, output is not hard-coded to a file; callers supply an output callback and argument when creating the trace VFS. The module is intended for embedding in applications or the SQLite shell to observe exact VFS call sequences and return codes.

Tracing is controlled by a bitmask and can be changed at runtime through `PRAGMA vfstrace(...)`, which is intercepted as `SQLITE_FCNTL_PRAGMA`. Individual VFS APIs can be enabled or disabled by name.

## Important APIs, Types, And Functions

- `vfstrace_register(zTraceName, zOldVfsName, xOut, pOutArg, makeDefault)` allocates a new `sqlite3_vfs` plus `vfstrace_info`, wraps the named or default underlying VFS, and registers the new shim.
- `vfstrace_unregister(zTraceName)` unregisters and frees a trace VFS only if its `xOpen` is `vfstraceOpen`.
- `vfstrace_info` stores the root VFS, output callback, trace mask, on/off flag, callback argument, VFS name, and pointer to the wrapper VFS.
- `vfstrace_file` stores per-open state: wrapper base, `pInfo`, display filename tail, and inline real file object.
- `VTR_*` constants define trace-mask bits for file, shared-memory, mmap, dynamic loading, randomness, sleep, time, last-error, and VFS-level operations.
- `vfstrace_printf`, `vfstrace_print_errcode`, and `vfstrace_errcode_name` centralize formatted output and symbolic SQLite result names.
- `vfstraceFileControl` decodes many `SQLITE_FCNTL_*` opcodes, implements runtime `vfstrace` pragma parsing, and wraps `SQLITE_FCNTL_VFSNAME` output.
- `vfstraceOpen` dynamically copies only the real file methods supported by the underlying file method version and installs wrappers for methods that exist.

## Control Flow

Registration finds the root VFS, allocates one block containing `sqlite3_vfs`, `vfstrace_info`, and the VFS name, copies version/path-size information, sets wrapper callbacks conditionally for optional VFS methods, initializes the trace mask to all bits, emits an `enabled_for` line, and registers the VFS.

For `xOpen`, the wrapper stores the basename-like file tail, delegates to the root VFS, then if the real file has methods, allocates a fresh `sqlite3_io_methods` table for that file. This table mirrors the underlying method version and points supported methods to trace wrappers. On successful `xClose`, the dynamically allocated method table is freed.

Each wrapped method calls `vfstraceOnOff` with its mask, prints the call and decoded arguments if enabled, delegates to the real method, and prints the result. File controls include special formatting for size hints, mmap sizes, WAL/blocking controls, pragma controls, and returned values. The `vfstrace` pragma accepts numeric masks or names with `+`/`-`, ignores non-alpha separator characters, and accepts names with optional leading `x`.

## State And Persistence Behavior

All state is process-local. A registered trace VFS persists until explicitly unregistered or process exit. `vfstrace_info::mTrace` and `bOn` are mutable through pragma calls and affect all files using that trace VFS. Per-file method tables are heap allocated at open time and freed only after successful close. Trace output persistence is entirely defined by the caller's `xOut` callback.

The wrapper does not own the underlying VFS. It stores raw pointers to the root VFS and output callback/argument, so caller-provided state must outlive the registered trace VFS.

## Dependencies And Integration Points

The implementation uses SQLite's public VFS API, file I/O API, syscall override hooks for VFS version 3, and many `SQLITE_FCNTL_*` constants. It expects `sqlite3.h` to provide SQLite typedefs/macros and relies on C library formatting, `strtoll`, `isalpha`, and string utilities. It integrates with the shell's `-vfstrace` support or any embedding application that calls `vfstrace_register`.

## Risks And Edge Cases

- The output callback is called with messages allocated by `sqlite3_vmprintf`; failures are not checked before invoking `xOut`.
- `vfstraceOpen` allocates a method table after the real open; allocation failure is not handled before `memset`, so this diagnostic code assumes allocation succeeds.
- `vfstraceCheckReservedLock` has a format string expecting an extra `%d` but does not pass `*pResOut` before delegation; this is a diagnostic formatting defect.
- A typo in the pragma keyword table uses `"shmummap"` rather than `"shmunmap"`, so the intuitive spelling may not toggle that mask.
- Runtime mask state is stored on the shared VFS info object, not per connection.
- `vfstrace_unregister` can free a VFS while clients still hold open files if called incorrectly.
- Only path tails are printed for file methods, which is concise but can be ambiguous.

## Test Signals

Tests should register a trace VFS with a buffer-backed callback, open a database through it, and assert expected call lines and symbolic result names. Specific signals include `xOpen` method-table wrapping, `xClose` freeing, `xFileControl(SQLITE_FCNTL_VFSNAME)`, `PRAGMA vfstrace('-all,+Lock,Unlock')`, WAL shared-memory calls when supported, mmap fetch/unfetch when supported, unregister behavior, and preservation of root VFS return codes.
