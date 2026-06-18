# sources/user-network-fs/samba/source3/libsmb/libsmb_thread_posix.c

Purpose: installs Samba's built-in POSIX pthread implementation for the libsmbclient thread abstraction.

Important API/state: `SMB_THREADS_DEF_PTHREAD_IMPLEMENTATION(tf)` defines a static pthread-backed `struct smb_thread_functions` table. `smbc_thread_posix()` passes that table to `smb_thread_set_functions()`. The file undefines a possible malloc macro before the pthread implementation macro to avoid malloc checker interference.

Control flow and dependencies: if pthread headers are available they are included; the implementation macro supplies the actual mutex/TLS functions. There is no allocation or runtime branching in `smbc_thread_posix()` itself. It integrates with the same global Samba thread function registry used by `smbc_thread_impl()`.

Risks: this is a process-level installation choice and should be called before concurrent context use. Build coverage depends on pthread availability and macro expansion in Samba headers. Test signals: call `smbc_thread_posix()` before `smbc_new_context()`, create/free contexts from multiple threads, verify `SMB_THREAD_ONCE` initializes the module once, and run under thread sanitizers for context-count mutex use.
