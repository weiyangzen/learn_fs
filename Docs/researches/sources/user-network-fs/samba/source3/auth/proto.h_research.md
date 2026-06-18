# sources/user-network-fs/samba/source3/auth/proto.h

## Purpose
This generated-style header declares the source3 auth subsystem's cross-file API. It connects the dispatcher, backends, server-info conversion, token utilities, user mapping, Kerberos helpers, PAM/plaintext checks, and source4 bridge.

## Important APIs, Types, and Functions
It declares auth registration/context APIs, GENSEC/auth4 preparation, NTLMSSP hook functions, SAM checks, backend init functions, user-info constructors, server-info and session-info constructors, token creation utilities, group/user membership helpers, PAM and plaintext password functions, Kerberos mapping functions, and `auth_samba4_init`. It also defines Unix hint flags such as `AUTH3_UNIX_HINT_QUALIFIED_NAME`, `AUTH3_UNIX_HINT_DONT_TRANSLATE_FROM_SIDS`, and `AUTH3_UNIX_HINT_DONT_EXPAND_UNIX_GROUPS`.

## Control Flow
The header itself has no runtime flow, but it documents call layering: callers build `auth_usersupplied_info`, create an `auth_context` or `auth4_context`, check credentials, receive `auth_serversupplied_info`, then convert to SamInfo or `auth_session_info` and tokens. It also exposes backend initialization for static module registration.

## State and Persistence
No state is stored in the header. The declarations expose stateful facilities implemented elsewhere, including backend registries, cached guest/system sessions, passdb mutation, PAM sessions, and token/session-key handling.

## Dependencies and Integration Points
The header forwards or references `TALLOC_CTX`, `DATA_BLOB`, `tsocket_address`, `samu`, `passwd`, Netlogon SamInfo structures, PAC structures, winbind auth info, security tokens, and Samba auth types. Some declared functions are outside this work item, so this file is the integration map for the wider auth directory.

## Risks and Test Signals
Risks include prototype drift from implementations, typo-preserved ABI names such as `AUTH3_UNIX_HINT_ISLOLATED_NAME`, and broad coupling that allows changes in one auth file to break many callers. Test signals are compile coverage, static module linkage, include hygiene, and end-to-end auth tests that exercise declarations across translation units.
