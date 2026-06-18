# sources/user-network-fs/samba/source4/torture/ldap/session_expiry.c

## Purpose

`session_expiry.c` verifies that a Kerberos-authenticated LDAP session fails after a deliberately short requested GSSAPI ticket lifetime.

## Important APIs, Types, and Functions

- `torture_ldap_session_expiry()` is the single entry point.
- `cli_credentials_set_kerberos_state(... CRED_USE_KERBEROS_REQUIRED ...)` forces Kerberos authentication.
- `lpcfg_set_option("gensec_gssapi:requested_life_time=4")` requests a four-second lifetime.
- `ldb_wrap_connect()` opens the authenticated LDAP-backed LDB connection.
- Repeated `ldb_search()` calls test behavior until expiry.

## Control Flow

The test builds `ldap://<host>/`, forces Kerberos credentials, sets the GSSAPI requested lifetime to four seconds, connects, performs an initial RootDSE search, then loops once per second for up to ten seconds. It stops when a search fails and asserts the final error is `LDB_ERR_PROTOCOL_ERROR`.

## State and Persistence Behavior

The test is read-only. It mutates process/test credential and loadparm state by forcing Kerberos and setting a GSSAPI lifetime option. Runtime state is the LDAP session and repeated search result allocation.

## Dependencies and Integration Points

It depends on Samba credentials, GENSEC GSSAPI options, LDAP-backed LDB, event context, RootDSE search behavior, and the LDAP suite registration.

## Risks and Edge Cases

Timing-sensitive behavior can be affected by KDC ticket policy, server clock, client retries, and LDAP/GSSAPI error mapping. The test expects protocol error after expiry, so changes to LDB's error translation can break it even if expiry still works.

## Test Signals

The expected signal is an initial successful RootDSE search, followed within ten seconds by `LDB_ERR_PROTOCOL_ERROR`. Continued success beyond the deadline or a different error indicates a regression or environment mismatch.
