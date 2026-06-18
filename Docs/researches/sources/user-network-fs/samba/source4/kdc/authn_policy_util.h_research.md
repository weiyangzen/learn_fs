# sources/user-network-fs/samba/source4/kdc/authn_policy_util.h

## Purpose

`authn_policy_util.h` exposes the KDC authentication policy utility API for feature gates, policy discovery, restriction enforcement, and audit-info construction.

## Important APIs, Types, and Functions

The header declares feature gates, assigned-silo lookup, Kerberos client policy lookup/enforcement, NTLM client policy lookup/enforcement, server policy lookup/enforcement, and restriction-present predicates. It defines `enum authn_policy_auth_type` with Kerberos and NTLM values, `struct authn_policy_flags` with `force_compounded_authentication`, and location-capturing macros `authn_kerberos_client_policy_audit_info()`, `authn_ntlm_client_policy_audit_info()`, and `authn_server_policy_audit_info()` around underscored implementations.

## Control Flow

Callers use lookup functions to obtain optional policy structs, then call the relevant enforcement or audit helper depending on the authentication path. The audit macros inject `__location__` so later audit records can identify the call site without each caller passing it manually.

## State and Persistence Behavior

Returned policy and audit structures are talloc-owned by the caller's context. The header carries no state, but it documents that `auth_user_info_dc` inputs must be talloc-allocated because implementations may keep references for audit logging.

## Dependencies and Integration Points

It includes replacement portability, public authentication policy/session types, and talloc. Forward declarations avoid exposing LDB and loadparm internals beyond pointer types. This header is consumed by KDC, NTLM, and claims code needing consistent policy behavior.

## Risks and Edge Cases

The API distinguishes `int` LDB-style lookup errors from `NTSTATUS` enforcement results, so callers must not conflate them. Audit output parameters are optional; callers that pass `NULL` lose diagnostics. The location macros should be used instead of underscored functions except when forwarding an existing location.

## Test Signals

Compile tests should catch declaration drift with the implementation. Runtime tests should verify optional `NULL` audit outputs, correct auth-type dispatch, and correct lifetime of returned policy/audit structures across temporary context cleanup.
