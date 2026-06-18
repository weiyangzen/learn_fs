<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/ntlm_auth_proto.h -->
# sources/user-network-fs/samba/source3/utils/ntlm_auth_proto.h

## Purpose

`ntlm_auth_proto.h` is the collected prototype header for `ntlm_auth.c` and `ntlm_auth_diagnostics.c`. It exposes the small cross-file API needed by diagnostics and any other utility code that links these helpers.

## Important APIs, Types, and Functions

The header declares winbind metadata helpers `get_winbind_domain()` and `get_winbind_netbios_name()`, challenge generation `get_challenge()`, challenge/response authentication `contact_winbind_auth_crap()`, diagnostics entry point `diagnose_ntlm_auth()`, and `get_pam_winbind_config()`.

## Control Flow

There is no runtime control flow. The declared functions participate in `ntlm_auth` command execution: `main()` calls diagnostics, diagnostics call challenge/auth helpers, and auth helper functions contact winbind.

## State and Persistence Behavior

Declared functions operate on process-global state in `ntlm_auth.c` for defaults, options, and cached winbind details. `contact_winbind_auth_crap()` may request session keys or Unix names and can allocate error strings and Unix-name strings for the caller.

## Dependencies and Integration Points

Consumers must include Samba base types for `DATA_BLOB`, `TALLOC_CTX`, and `NTSTATUS`. The interface is tightly coupled to winbind protocol flags, NTLM response blobs, and Samba memory ownership conventions.

## Risks and Edge Cases

Because this is a frozen generated-style prototype header, API drift can happen if function signatures change without updating it. `contact_winbind_auth_crap()` ownership semantics are easy to misuse: output strings are heap-allocated and must be freed by the caller, and optional session-key buffers must be valid when their flags are requested.

## Test Signals

Compile tests should catch signature drift. Runtime checks should exercise `contact_winbind_auth_crap()` with and without `WBFLAG_PAM_LMKEY`, `WBFLAG_PAM_USER_SESSION_KEY`, and `WBFLAG_PAM_UNIX_NAME` to verify optional outputs and ownership.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/ntlm_auth_proto.h -->
