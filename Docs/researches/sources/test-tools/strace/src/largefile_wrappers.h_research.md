# sources/test-tools/strace/src/largefile_wrappers.h

Purpose: abstracts libc large-file API name differences behind strace-local wrapper names.

Important APIs/types/functions: `open_file`, `fopen_stream`, `fcntl_fd`, `fstat_fd`, `strace_stat_t`, `lstat_file`, `stat_file`, `struct_dirent`, `read_dir`, `struct_rlimit`, and `set_rlimit`.

Control flow: if `_LARGEFILE64_SOURCE` is enabled, wrapper macros select `*64` variants when available or appropriate; otherwise they map to regular libc calls and types.

State and persistence behavior: no state; compile-time macro aliases only.

Dependencies and integration points: includes `defs.h` for configure macros such as `HAVE_OPEN64`, `HAVE_FOPEN64`, and `HAVE_FCNTL64`. Used by host-side strace code that needs large-file-capable filesystem and resource-limit APIs.

Risks: availability differs by libc and architecture, so wrappers must avoid referencing missing symbols. Mixing wrapper and raw libc names can reintroduce large-file bugs.

Test signals: build with and without `_LARGEFILE64_SOURCE`, run host filesystem operations on large files, and compile on libcs lacking selected `*64` entry points.
