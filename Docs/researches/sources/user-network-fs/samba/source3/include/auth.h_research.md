# sources/user-network-fs/samba/source3/include/auth.h

## Purpose
`auth.h` defines source3 authentication server-side structures and module interfaces. It standardizes how authentication methods receive user-supplied info, return server-supplied session data, prepare GENSEC/auth4 contexts, and register auth modules.

## Important APIs, Types, And Functions
- `struct extra_auth_info` holds non-normal user and primary group SIDs.
- `struct auth_serversupplied_info` carries guest status, Unix security token, optional cached session info, session keys, Netlogon info3, extra SID info, NSS token flag, and Unix name.
- `prepare_gensec_fn` and `make_auth4_context_fn` callbacks bridge source3 auth to GENSEC and auth4.
- `struct auth_context` holds challenge data, start time, challenge origin, ordered auth method list, Netlogon mode, and context-preparation callbacks.
- `struct auth_methods` is a linked-list module entry with `auth()` callback, optional GENSEC/auth4 callbacks, private data, and flags.
- `auth_init_function` and `auth_init_function_entry` define module initialization.
- `AUTH_INTERFACE_VERSION` is `5`.
- `enum session_key_use_intent` distinguishes full vs 16-byte session key use.

## Control Flow
An auth subsystem builds an `auth_context`, loads `auth_methods`, and invokes each method's `auth()` callback until a result is accepted or all fail. Optional callbacks produce GENSEC or auth4 contexts for higher-level negotiation.

## State And Persistence
Structures are request/session state and talloc-owned by callers. No storage is implemented, but returned tokens and session keys feed persisted sessions and authorization decisions elsewhere.

## Dependencies And Integration Points
It depends on common auth definitions, Unix security tokens, Netlogon generated types, GENSEC, auth4, DATA_BLOB, and generated `auth/proto.h`. Authentication modules must match `AUTH_INTERFACE_VERSION`.

## Risks
Session key handling is security-critical. The cached session-info shortcut is documented as atypical and should remain tightly controlled. Module ABI/version drift can break dynamically loaded auth modules.

## Test Signals
Test module registration/version checks, ordered method fallback, guest/system cached session handling, Netlogon info3-derived tokens, extra SID edge cases, session key intent truncation, and GENSEC/auth4 preparation.
