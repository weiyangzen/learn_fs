# sources/user-network-fs/samba/source3/lib/netapi/netapi.c

## Purpose

`netapi.c` implements libnetapi context lifecycle, configuration/logging hooks, credential setters/getters, error-string helpers, and NetAPI buffer allocation/free. It was read as a complete 541-line file. This is the process-level support layer used by all public wrappers and implementation files.

## Important APIs, Types, and Functions

Core functions are `libnetapi_init_private_context()`, `libnetapi_init()`, `libnetapi_net_init()`, `libnetapi_getctx()`, `libnetapi_free()`, `libnetapi_set_debuglevel()`, `libnetapi_set_logfile()`, credential accessors/mutators (`libnetapi_get_username`, `libnetapi_get_password`, `libnetapi_set_username`, `libnetapi_set_password`, `libnetapi_set_workgroup`, `libnetapi_set_creds`, `libnetapi_get_creds`, `libnetapi_set_use_kerberos`, `libnetapi_get_use_kerberos`, `libnetapi_set_use_ccache`), `libnetapi_errstr()`, `libnetapi_set_error_string()`, `libnetapi_get_error_string()`, `NetApiBufferAllocate()`, and `NetApiBufferFree()`. Global state is `stat_ctx` and `libnetapi_initialized`.

## Control Flow

`libnetapi_init()` is for non-Samba applications: it initializes loadparm, forces log level 0, loads `smb.conf`, loads interfaces, reopens logs, blocks SIGPIPE, and delegates to `libnetapi_net_init()`. `libnetapi_net_init()` creates or returns the singleton context, initializes or accepts credentials, guesses defaults, creates private data, steals the context to the null talloc root, and records it globally. `libnetapi_free()` tears down SAMR caches, connection manager state, loadparm/charset/interface/secrets/netlogon/debug resources, and frees the context.

## State and Persistence Behavior

This file owns process-global libnetapi state through the singleton context. The context stores loadparm state, credentials, debug/logfile strings, private data, and a context error string. Initialization loads persistent configuration and secrets; freeing shuts down secrets and global databases. `NetApiBufferAllocate()` allocates talloc memory at the null root for Windows-style API buffers, and `NetApiBufferFree()` frees those buffers.

## Dependencies and Integration Points

Dependencies include Samba loadparm, credentials, gensec, secrets, netlogon credential database, connection manager/SAMR cleanup helpers, debug logging, talloc, and error conversion utilities. All wrappers in `libnetapi.c` call `libnetapi_getctx()`, and implementation files use context credentials and `libnetapi_set_error_string()`.

## Risks and Edge Cases

The singleton context is not obviously thread-isolated; credential/logging changes affect subsequent callers in the process. `libnetapi_free()` resets `stat_ctx` but does not set `libnetapi_initialized` back to false in this file, so reinitialization semantics depend on the `stat_ctx` check path. Several setters assume non-null context or loadparm fields. `NetApiBufferFree(NULL)` returns `WERR_INSUFFICIENT_BUFFER`, which differs from many C free conventions. Error-string storage is one-per-context and overwritten on each set.

## Test Signals

Tests should cover repeated `libnetapi_init()` idempotence, `libnetapi_free()` followed by re-init, credential setter/getter behavior, Kerberos/ccache flags, debug/logfile configuration, `libnetapi_get_error_string()` with and without explicit error strings, zero/nonzero buffer allocation, null free behavior, and wrapper calls after context initialization from both standalone and `net`-embedded paths.
