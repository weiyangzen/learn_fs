# sources/user-network-fs/samba/source3/libsmb/libsmb_setget.c

Purpose: provides the public getter/setter surface for `SMBCCTX` options, global-ish logging/config hooks, server cache callbacks/data, and all operation function pointers. It is the customization layer that lets callers replace libsmbclient behavior per context.

Important APIs: simple string setters/getters manage NetBIOS name, workgroup, and user. Option APIs cover debug, timeout, port, stderr logging, full time names, share mode, user data, encryption level, case sensitivity, browse LMB count, readdir URL encoding, one-share-per-server, Kerberos/fallback/anonymous/ccache/NT-hash flags, protocol min/max, and POSIX extensions. Function pointer APIs get/set auth, server cache, file, directory, xattr, statvfs, truncate, notify, and print callbacks.

Control flow/state: most setters directly mutate `SMBCCTX` or `SMBC_internal_data`; string setters free and duplicate. `smbc_setDebug()` also updates loadparm command-line log level. `smbc_setOptionDebugToStderr()` switches process logging to stderr and is intentionally sticky. `smbc_setConfiguration()` loads a config file without full reinit. Protocol setters write loadparm settings in the context loadparm object.

Dependencies and integration: includes `libsmbclient.h`, `libsmb_internal.h`, and loadparm APIs. `smbc_new_context()` calls these setters to install defaults, and compatibility wrappers call the getters for dispatch.

Risks: few functions validate null context pointers or allocation failure, so callers must pass initialized contexts. Some options are process-wide in effect despite context-scoped names. Callback replacement can break invariants if custom implementations do not maintain `context->internal->files` or cache contracts. Test signals: each flag bit toggles independently, string setters handle NULL, debug updates loadparm, stderr stickiness, protocol invalid values return false, callback overrides are invoked, server cache data round-trips, and default callbacks match context initialization.
