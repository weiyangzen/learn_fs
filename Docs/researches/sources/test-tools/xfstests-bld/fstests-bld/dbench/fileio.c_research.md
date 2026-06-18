<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/fileio.c -->
# sources/test-tools/xfstests-bld/fstests-bld/dbench/fileio.c

Source read: complete file, 622 lines, 13907 bytes, sha256 `8d7f185e9b229bf7070a11e7e8559cebf4820874e2823d4ed592633684e62f06`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/dbench/fileio.c_research.md`.

Purpose: implements the dbench direct filesystem replay backend. It translates SMB-like trace operations into local POSIX file, directory, xattr, stat, locking, and fsync calls while maintaining each synthetic client's open-handle table and byte counters.

Important APIs/types/functions: `nb_setup()` allocates a 200-entry `struct ftable` in `child->private`; `find_handle()` resolves trace handles to file descriptors; `sync_parent()` fsyncs/fdatasyncs a containing directory for NFS-like synchronous metadata behavior; `resolve_name()` optionally simulates case-insensitive name resolution and xattr reads. The exported `nb_*` functions implement unlink, mkdir, rmdir, create/open, read, write, close, rename, flush, path/file/fs info probes, findfirst, deltree cleanup, fileinfo updates, byte-range locks, unlocks, and sleeps.

Control flow: trace runner calls `nb_setup()` once per child, then dispatches parsed trace records to the relevant `nb_*` function. Open/create paths compute POSIX flags from SMB create disposition/options, handle directory special cases, store descriptors in the ftable, and initialize optional DOS-attribute xattrs. Read/write/flush/lock paths first resolve a handle, operate on the descriptor, update byte counters, and abort on hard mismatches. Metadata operations often call `resolve_name()` first, compare actual return values with `expected_status()`, and optionally sync the parent directory after mutating operations.

State and persistence behavior: persistent effects are intentional benchmark filesystem mutations under each child directory: files, directories, renames, truncations, timestamps, locks while descriptors are open, and optional `user.DosAttrib` extended attributes. In-memory state includes per-child ftable slots, `child->bytes`, `child->bytes_since_fsync`, failure flags, and rate timing. `nb_cleanup()` recursively removes the child tree unless higher-level options skip cleanup.

Dependencies and integration: includes `dbench.h`, uses `options` for sync, fsync, xattr, stat-check, fake-I/O, no-resolve, one-byte-write, and cleanup behavior, calls xattr wrappers from `system.c`, time helpers from `util.c`, and generated prototypes from `proto.h`. It must not be linked with `sockio.c` in the same executable because both provide the same `nb_*` symbols.

Risks: `resolve_name()` leaks `dname` when no slash is present; `nb_findfirst()` mutates the supplied `fname` buffer despite receiving a `const char *`; `nb_deltree()` skips freeing `fname` on stat failure; many system-call return values are ignored when status comparison is not central; xattr writes cast a byte buffer to `time_t *`, which can be alignment-sensitive. The fixed 200-open-file table can abort on traces with more concurrent handles.

Test signals: replay traces should validate create/read/write byte counts, expected-status handling for failing operations, cleanup idempotence, directory fsync behavior with `sync_dirs`, `fake_io` accounting, and xattr-enabled runs on filesystems with and without user xattr support.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/fileio.c -->
