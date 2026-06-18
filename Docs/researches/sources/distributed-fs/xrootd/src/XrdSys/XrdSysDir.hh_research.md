## sources/distributed-fs/xrootd/src/XrdSys/XrdSysDir.hh

Purpose: declares the `XrdSysDir` directory iteration API.

Important APIs/types/functions: constructor `XrdSysDir(const char *path)`, virtual destructor, `bool isValid()`, `int lastError()`, and `char *nextEntry()`. The private state is an opaque `void *dhandle` plus `lasterr`.

Control flow: callers construct an instance, check `isValid()`, loop on `nextEntry()`, and inspect `lastError()` if null is returned unexpectedly.

State and persistence: object-scoped directory handle only. No persistent filesystem mutation is performed by this class.

Dependencies and integration: includes `sys/types.h` on non-Windows and defines `uid_t`/`gid_t` aliases for Windows. It hides the platform-specific directory handle behind `void *`.

Risks: inline accessors expose no synchronization, so each instance is single-consumer unless externally serialized. The `char *` return type suggests mutable data even though callers should not modify platform buffers.

Test signals: compile on Windows and Unix, validate destructor closes resources, and assert `lastError()` distinguishes invalid construction from normal iteration exhaustion.
