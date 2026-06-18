# sources/user-network-fs/samba/source4/ntvfs/unixuid/vfs_unixuid.c

Purpose: `vfs_unixuid.c` implements the `unixuid` NTVFS pass-through module. It wraps downstream NTVFS operations with effective Unix UID/GID/group changes derived from the authenticated SMB session token.

Important APIs, types, and functions: Key pieces are `unixuid_private`, `save_unix_security`, `set_unix_security`, `unixuid_event_nesting_hook`, `nt_token_to_unix_security`, `unixuid_setup_security`, the `PASS_THRU_REQ` macro, wrapper functions for most NTVFS operations, and `ntvfs_unixuid_init`.

Control flow: On connect, the module stores private cache state, installs a tevent nesting hook, and calls the next backend as root so it can initialize databases. For normal requests, `PASS_THRU_REQ` saves the current Unix credentials, converts or reuses the session security token's Unix token, sets effective groups/gid/uid, calls `ntvfs_next_*`, then restores the saved context. The nesting hook temporarily returns to root when nested event loops begin and restores caller credentials afterward.

State and persistence behavior: Runtime state caches the last NT security token and corresponding Unix token per module instance. A global nesting counter tracks whether the event nesting hook must act. Persistent file effects are performed by downstream modules under the switched Unix credentials.

Dependencies and integration points: It depends on auth token conversion, wbclient, NTVFS pass-through APIs, tevent nesting hooks, and Samba setid wrappers. It registers for disk, print, and IPC backend types.

Risks: Credential switching is security-critical; any missed restore can leave the server in the wrong effective identity. The global nesting counter interacts with per-connection state and nested async processing. The cache compares token pointers, so token lifetime and reuse matter.

Test signals: Tests should verify operations execute as the session Unix identity, credentials restore on success and failure, nested tevent callbacks restore correctly, logoff clears cached token, and all registered backend types pass through as expected.
