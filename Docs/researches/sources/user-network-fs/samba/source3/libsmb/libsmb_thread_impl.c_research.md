# sources/user-network-fs/samba/source3/libsmb/libsmb_thread_impl.c

Purpose: exposes a generic hook for applications to install arbitrary mutex and thread-local-storage primitives for Samba's thread abstraction used by libsmbclient.

Important API: `smbc_thread_impl()` accepts seven function pointers: create/destroy/lock mutex and create/destroy/set/get TLS. It stores them in a static `struct smb_thread_functions tf` and passes that table to `smb_thread_set_functions()`.

Control flow/state: the function performs no validation despite the comment saying all pointers are required. The static table persists after the call, so Samba's thread layer references stable storage. Repeated calls overwrite the same static function table.

Dependencies and integration: depends on `../lib/util/smb_threads_internal.h` for `smb_thread_set_functions` and the table shape. `libsmb_context.c` relies on the installed thread functions for `SMB_THREAD_ONCE`, mutex creation, and locking around global context counts.

Risks: null or incompatible callbacks can break later context initialization or global locking. Calling this after contexts are already active may change synchronization semantics mid-process. Tests should install mock functions before `smbc_new_context()`, assert once/mutex/TLS calls route through the mock layer, exercise repeated replacement, and check behavior when callbacks report failure.
