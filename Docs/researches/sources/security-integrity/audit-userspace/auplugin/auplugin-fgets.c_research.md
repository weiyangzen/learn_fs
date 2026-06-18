<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auplugin/auplugin-fgets.c -->
# sources/security-integrity/audit-userspace/auplugin/auplugin-fgets.c

Purpose: descriptor-based replacement for `fgets`, designed for audit plugin input streams and reusable both as global state and as reentrant state objects.

Important APIs and functions: `auplugin_fgets_init/destroy`, `_clear_r`, `_eof_r`, `_more_r`, `_fgets_r`, and `_setvbuf_r` implement the reentrant API; global wrappers lazily initialize `global_state`. `enum auplugin_mem` controls ownership for internal, malloc, mmap, and read-only mmap-file buffers.

Control flow and state: each state tracks `buffer`, `current`, `eptr`, `orig`, `eof`, memory type, and buffer size. `auplugin_fgets_r` first returns buffered complete lines, reads only when needed, compacts unread data only when out of room, returns partial data at EOF or capacity, and advances permanently for `MEM_MMAP_FILE`.

Dependencies and integration: used by `auplugin.c` inbound handling to frame audit records from a nonblocking fd. Relies on `read`, `munmap`, libaudit size constants through `auplugin.h`.

Risks and test signals: risks are off-by-one NUL handling, EOF semantics, ownership mismatch, and global API non-reentrancy. Dedicated `fgets_test` and `fgets_r_test` cover line, partial, long, custom-buffer, and mmap-file paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auplugin/auplugin-fgets.c -->
