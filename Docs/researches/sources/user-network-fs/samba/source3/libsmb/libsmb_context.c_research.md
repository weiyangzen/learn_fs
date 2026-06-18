# sources/user-network-fs/samba/source3/libsmb/libsmb_context.c

Purpose: owns libsmbclient module initialization, context allocation, default option/callback installation, context initialization, teardown, deprecated option compatibility, version reporting, and credential refresh for DFS-aware operations.

Important APIs/state: static `SMBC_initialized`, `initialized_ctx_count`, and `initialized_ctx_count_mutex` protect module lifetime. `SMBC_module_init()` configures logging, loads `$HOME/.smb/smb.conf`, global config, optional append config, interfaces, SIGPIPE blocking, and the context-count mutex. `smbc_new_context()` allocates `SMBCCTX`, `SMBC_internal_data`, talloc/loadparm context, then installs defaults for options and all major operation callbacks. `smbc_init_context()` fills user/netbios/workgroup defaults and marks a context initialized. `smbc_free_context()` performs polite or aggressive cleanup. `smbc_set_credentials_with_fallback()` builds `cli_credentials` using Kerberos, fallback, ccache, and password settings.

Control flow and persistence: module init runs through `SMB_THREAD_ONCE`. Each initialized context increments a global count under the mutex; free decrements and calls `SMBC_module_terminate()` when it reaches zero. Context persistent state includes open file list, server list/cache, options, callback table, loadparm context, and current credentials. Aggressive free closes files and forcibly shuts down cached servers; polite free refuses with `EBUSY` if files or servers remain.

Dependencies and integration: includes Samba client, socket, secrets, credentials, gensec, loadparm, and thread helper APIs. It is the composition root for default implementations in the other libsmb files.

Risks: global logging/stderr and config are process-wide despite per-context APIs. The `LIBSMBCLIENT_NO_CCACHE` option logic is subtle and should be tested for default ccache behavior. Test signals: missing auth callback rejected, timeout clamped, user/netbios/workgroup defaulting, polite `EBUSY`, aggressive shutdown, module termination after last context, deprecated option set/get, and Kerberos/fallback credential fields.
