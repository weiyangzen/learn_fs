# sources/user-network-fs/samba/source4/torture/ldap/ldap_sort.c

## Purpose

`ldap_sort.c` tests LDAP server-side sorting through LDB controls. It queries the `cn=users` subtree sorted by `cn` and validates returned entries are in case-insensitive ascending order with whitespace handling approximating Samba's sort behavior.

## Important APIs, Types, and Functions

- `torture_ldap_sort()` is the only test entry point.
- `ldb_wrap_connect()` creates an authenticated LDAP-backed LDB connection.
- `ldb_server_sort_control` defines the sort key, here `cn`, no ordering rule, not reversed.
- `ldb_build_search_req()`, `ldb_request_add_control()`, `ldb_request()`, and `ldb_wait()` drive the controlled search.

## Control Flow

The test connects to `ldap://<host>/`, builds a subtree search under default basedn plus `cn=users`, attaches a critical `LDB_CONTROL_SERVER_SORT_OID`, executes and waits for completion, then iterates results. For each entry it finds `cn`, prints it, and compares it to the previous value using `toupper_m()` while accounting for repeated leading/trailing spaces.

## State and Persistence Behavior

The test is read-only. Runtime state is the LDB request/result and previous/current `cn` values.

## Dependencies and Integration Points

It depends on LDB controls, LDAP-backed LDB connection setup, Samba UTF/case helpers, command-line credentials, and the LDAP suite registration in `common.c`.

## Risks and Edge Cases

The comparison is intentionally limited to ASCII-ish behavior and ad hoc whitespace handling, while the server may implement richer collation. It requires at least two results for ordering assertions. Missing `cn` attributes fail the test.

## Test Signals

Success means the server accepted the critical sort control, returned search results, every result had `cn`, and the local comparison did not detect descending order. Failures identify sort-control regressions or collation mismatches.
