# sources/user-network-fs/samba/source3/lib/cmdline_contexts.c

Purpose: provides command-line tools with a safe way to obtain Samba's global messaging context.

Important APIs/types/functions: `cmdline_messaging_context()` and `cmdline_messaging_context_free()`.

Control flow: the getter ensures loadparm is initially loaded, then enforces that clustering mode only runs as root because CTDB/registry/messaging access requires privileges. It returns `global_messaging_context()`, exiting on root initialization failure while allowing non-root non-cluster callers to handle a null result.

State and persistence: uses global loadparm and global messaging context state; no file persistence.

Dependencies/integration: loadparm, global contexts, messaging, `geteuid()`, stderr, process exit.

Risks/test signals: this helper can terminate the process for clustered non-root or root messaging-init failures. Tests should exercise config-load failure, non-root non-cluster null handling, clustered non-root exit, root init failure exit, and free delegating to `global_messaging_context_free()`.
