# sources/user-network-fs/samba/source4/torture/ldap/basic.c

## Purpose

`basic.c` implements low-level LDAP protocol torture tests against a Samba AD LDAP server. It validates RootDSE searches, substring filter behavior, simple and SASL bind behavior, compare operations, AD-style error message mappings, referral generation, and abandon request handling.

## Important APIs, Types, and Functions

- `test_bind_sasl()` wraps `torture_ldap_bind_sasl()` with command-line credentials.
- `test_multibind()` verifies anonymous bind followed by a simple authenticated bind on the same connection is rejected with `LDAP_STRONG_AUTH_REQUIRED`.
- `test_search_rootDSE()` sends a raw LDAP base-scope RootDSE search and extracts `defaultNamingContext` and `namingContexts`.
- `test_search_rootDSE_empty_substring()` and `test_search_auth_empty_substring()` force an empty substring filter on `objectclass`.
- `test_compare_sasl()` sends an LDAP compare request for `objectClass=domain`.
- `ad_error()` parses Windows hex error prefixes from LDAP error messages.
- `test_error_codes()` sends intentionally invalid add/modify/delete/modifyDN requests and checks LDAP result codes, AD WERRORs, and referrals.
- `test_referrals()` uses an LDB LDAP connection to verify base, onelevel, and subtree referral generation across naming contexts.
- `test_abandon_request()` sends an AbandonRequest for an old message id.
- `torture_ldap_basic()` orchestrates the full test.

## Control Flow

The test connects to `ldap://<host>/`, performs RootDSE discovery, then runs a sequence of independent protocol checks while accumulating `ret`. It first tests RootDSE and substring search handling, then binding rules, then authenticated search and compare. Error-code testing reuses one `ldap_message` object to submit malformed operations and validates both the LDAP result code and Samba's AD-compatible diagnostic text. Referral testing walks every non-root naming context and checks which parent partition searches should or should not emit referral URLs under base, onelevel, and subtree scopes. The connection is closed via a real UnbindRequest through `torture_ldap_close()`.

## State and Persistence Behavior

The test should not intentionally persist directory data. It sends malformed add/modify/delete/rename requests against protected or invalid DNs and expects failure. Referral and search checks are read-only. Connection authentication state changes during anonymous, simple, and SASL bind attempts.

## Dependencies and Integration Points

It uses Samba's raw LDAP client (`ldap_connection`, `ldap_message`, `ldap_request_send`, `ldap_result_one`), LDB LDAP wrapper for referral checks, command-line credentials, torture LDAP helpers from `common.c`, and LDAP/LDB result constants. It is registered as `ldap.basic` in `torture_ldap_init()`.

## Risks and Edge Cases

The expected AD diagnostic WERRORs allow some version-dependent alternatives, but changes in LDAP error text formatting can still break parsing. Referral checks depend on `namingContexts` ordering and URL formatting. The multi-bind expectation relies on server policy requiring stronger auth after anonymous bind. Reusing message objects across malformed operations requires every field to be reset carefully.

## Test Signals

Signals include successful RootDSE extraction, expected failure of second simple bind, successful SASL bind, successful compare request, exact LDAP result/WERROR pairs for malformed operations, required and forbidden referral URLs by scope, successful abandon wait, and clean unbind.
