<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_statfs.c -->
# sources/test-tools/strace/src/print_statfs.c

Purpose: prints normalized `statfs` and `statfs64` structures.

Important APIs/types/functions: `print_struct_statfs`, `print_struct_statfs64`, `print_f_fsid`, `fetch_struct_statfs`, `fetch_struct_statfs64`, `fsmagic`, and `statfs_flags`.

Control flow: fetches the requested statfs variant into `struct strace_statfs`, prints filesystem type, block/file counts, optional fsid, name length, fragment size, and `f_flags` only when `ST_VALID` is set.

State and persistence behavior: no state.

Dependencies and integration points: used by statfs-family syscall decoders; depends on configure probes for structure fields and fetchers that normalize native/compat layouts.

Risks: optional fields vary by platform. Flag printing depends on `ST_VALID`; missing fetch support falls back to address.

Test signals: statfs/statfs64 success, magic type names, fsid layouts, flags with and without `ST_VALID`, invalid pointers, and platforms lacking statfs64.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_statfs.c -->
