# sources/user-network-fs/libtirpc/tirpc/reentrant.h

Purpose: `reentrant.h` maps historical BSD/Solaris RPC threading abstraction names onto pthread APIs for Linux and Apple builds.

Important APIs, types, and functions: It aliases `mutex_t`, `cond_t`, `rwlock_t`, `once_t`, and `thread_key_t`, defines initializer macros, and maps mutex, condition variable, rwlock, thread-local key, signal-mask, once, self, and exit operations to pthread calls.

Control flow: There is no runtime control flow in the header. Preprocessor control includes the mappings only when `__linux__` or `__APPLE__` is defined; other platforms are expected to use native headers or alternate definitions.

State and persistence behavior: The types represent synchronization and thread-local state owned by the calling modules. The header itself owns none.

Dependencies and integration points: `svc_vc.c` and other libtirpc internals use these aliases for global service locks and operation-table initialization. It depends on `<pthread.h>`.

Risks: The file explicitly says definitions are only guaranteed valid on Linux. Apple support is included by the condition but may differ in subtle pthread/rwlock availability behavior. Platforms outside the guard get no definitions.

Test signals: Build and thread-safety tests should cover global ops initialization, fd table locking, condition variable users, and platform preprocessor paths.
