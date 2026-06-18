<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/procattr.c -->
# sources/security-integrity/selinux/libselinux/src/procattr.c

## Purpose
Implements process security attribute getters and setters through `/proc/.../attr/*`, including current, previous, exec, fscreate, sockcreate, and keycreate contexts.

## Important APIs, Types, And Functions
`openattr()` chooses `/proc/<pid>/attr`, `/proc/thread-self/attr`, or `/proc/self/task/<tid>/attr`. `getprocattrcon_raw()` and `setprocattrcon_raw()` perform raw reads/writes. Macros generate `getcon`, `setcon`, `getexeccon`, `setexeccon`, `getfscreatecon`, `setsockcreatecon`, `getkeycreatecon`, and raw variants. `getpidcon*()` and `getpidprevcon*()` query other processes.

## Control Flow
Self setters translate contexts to raw form and cache successful writes in thread-local `prev_*` pointers. Self getters return cached values when present, otherwise read procfs. Clearing a context writes zero bytes.

## State And Persistence Behavior
Persistent effects are kernel per-thread/process procattr changes. Thread-local caches mirror recent successful writes and are freed by pthread-key destructors.

## Dependencies And Integration Points
Uses setrans translation, weak pthread helpers, `selinux_page_size`, `gettid()`/syscall fallback, and procfs ABI.

## Risks And Test Signals
Risks include cache staleness after external changes, pthread destructor behavior without pthreads, path buffer overflow protection, EINTR handling, and writing NULL buffers for clears. Tests should cover self and pid paths, clear/idempotent set, thread isolation, missing `/proc/thread-self`, invalid PIDs, and translated contexts.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/procattr.c -->
