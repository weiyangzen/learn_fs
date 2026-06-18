# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_auth.c

Read completely: 1187 lines.

Implements NetBSD’s core kauth credential and authorization-scope framework. It manages `kauth_cred_t` allocation, reference counting, cloning/copying, UID/GID/group accessors and mutators, credential fork/chroot hooks, conversion to/from legacy credential structures, secmodel-specific credential data keys, and current-LWP credential lookup.

The file also owns authorization scope registration and listener dispatch. `kauth_init()` creates the credential pool, specificdata domain, global `kauth_lock`, and built-in scopes for credential, generic, system, process, network, machdep, device, and vnode authorization. `kauth_register_scope()`, `kauth_deregister_scope()`, `kauth_listen_scope()`, and `kauth_unlisten_scope()` maintain the scope/listener queues. `kauth_authorize_action_internal()` calls each listener and aggregates allow/deny/defer results, with `NOCRED` and `FSCRED` short-circuited to allow.

Public wrappers map callers into specific built-in scopes: generic, system, process, network, machdep, device, tty, raw device, device passthrough, and vnode authorization. Vnode authorization distinguishes explicit listener allow/deny from filesystem decisions and remote-filesystem fallback behavior. Helper translators convert vnode access modes and extended-attribute modes into kauth vnode actions.

Risks and notes: listener traversal in `kauth_authorize_action_internal()` has reader locking commented out, so listener lifetime depends on wider kauth conventions. Credential setters assert exclusive ownership via `cr_refcnt == 1`. `kauth_proc_fork()` explicitly relies on the parent being stalled during fork. `kauth_proc_setgroups()` has an indentation oddity around the failure return but behavior is straightforward. If no secmodels are registered, deferred non-denied actions are allowed by `kauth_authorize_action()`.
