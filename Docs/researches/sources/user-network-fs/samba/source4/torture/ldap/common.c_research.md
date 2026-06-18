# sources/user-network-fs/samba/source4/torture/ldap/common.c

## Purpose

`common.c` provides shared LDAP torture helpers and registers the LDAP/CLDAP torture suite. It centralizes connection setup, simple/SASL bind wrappers, orderly unbind, and suite membership.

## Important APIs, Types, and Functions

- `torture_ldap_bind()` wraps `ldap_bind_simple()`.
- `torture_ldap_bind_sasl()` wraps `ldap_bind_sasl()`.
- `torture_ldap_connection()` allocates `ldap4_new_connection()` and connects to a URL.
- `torture_ldap_close()` sends an LDAP UnbindRequest and frees the connection.
- `torture_ldap_init()` registers `bench-cldap`, `basic`, `sort`, `cldap`, `netlogon-udp`, `netlogon-tcp`, `netlogon-ping`, `schema`, `uptodatevector`, `nested-search`, and `session-expiry`.

## Control Flow

Helper calls are thin wrappers that print diagnostics on failure and return `NTSTATUS`. Close builds a raw LDAP UnbindRequest, sends it, waits for completion, and frees the connection. Suite initialization creates the `ldap` suite, adds all simple tests, sets the description, and registers it with smbtorture.

## State and Persistence Behavior

This file owns connection lifetime but no persistent server state. `torture_ldap_close()` consumes and frees the connection even on unbind allocation/send failures.

## Dependencies and Integration Points

It depends on the raw LDAP client, torture suite API, loadparm context, command/event context from `struct torture_context`, and prototypes generated for the LDAP torture files. All LDAP tests in this folder integrate through this registration point.

## Risks and Edge Cases

The wrappers expose raw status without retries. `torture_ldap_close()` frees the connection on several error paths, so callers must not use it after close failure. Suite registration must stay synchronized with available test functions and build declarations.

## Test Signals

Build/link success confirms the shared prototypes. Runtime `smbtorture --list` or execution of the `ldap` suite confirms all tests are registered, and individual helpers surface bind/connect/unbind failures as `NTSTATUS` diagnostics.
