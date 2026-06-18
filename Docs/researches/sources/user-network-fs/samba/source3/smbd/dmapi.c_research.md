# sources/user-network-fs/samba/source3/smbd/dmapi.c

## Purpose
`dmapi.c` provides optional DMAPI/HSM integration. When compiled without DMAPI support, it returns no-op values. With DMAPI, it creates or reconnects to a long-lived kernel DMAPI session and reports offline file attributes by checking whether read events are registered on a file.

## Important APIs, types, and functions
- Non-DMAPI builds export stub `dmapi_file_flags()`, `dmapi_have_session()`, and `dmapi_get_current_session()`.
- `struct smbd_dmapi_context` stores the current `dm_sessid_t` and a numeric suffix for new session names.
- `dmapi_have_session()` lazily allocates global `dmapi_ctx` and initializes a session as root.
- `dmapi_new_session()` destroys/recreates an invalid session with an incremented name suffix.
- `dmapi_destroy_session()` tears down the kernel session during master smbd exit.
- `dmapi_file_flags()` maps DMAPI read-event interest to `FILE_ATTRIBUTE_OFFLINE`.

## Control flow
DMAPI initialization calls `dm_init_service()`, enumerates kernel sessions with a growable buffer, queries names looking for `samba` or `sambaN`, and creates a session if none matches. File flag lookup obtains the current session, optionally becomes root on systems without POSIX capabilities, converts a path to a DMAPI handle, retries after re-enabling capability on `EPERM`, reads the event list, and sets the offline bit if `DM_EVENT_READ` is present.

## State and persistence behavior
DMAPI sessions are persistent kernel resources and can outlive smbd worker processes. Samba caches the session in global `dmapi_ctx`. The file does not persist user data, but session creation/destruction affects kernel/HSM state.

## Dependencies and integration points
It depends on platform DMAPI headers, Samba privilege switching, `set_dmapi_capability()`, and VFS offline-attribute paths. GPFS or other HSM VFS modules may override or complement the default flag logic.

## Risks and edge cases
- Session lifetime is intentionally long; destroying too early can affect other smbd children, while never destroying can block HSM shutdown.
- Capability handling differs by platform and user ID changes can drop effective capabilities.
- `dmapi_file_flags()` receives a path string and can race with rename/unlink.
- DMAPI stubs mean callers must tolerate all-zero/no-session behavior.

## Test signals
Build tests should cover DMAPI and non-DMAPI configurations. Integration tests on a DMAPI/HSM-capable filesystem should verify session reuse, invalid-session recreation, offline flag detection, permission/capability retry, and master-process session destruction.
