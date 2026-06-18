# sources/user-network-fs/samba/source3/script/tests/test_wbinfo_u_large_ad.sh

Purpose: load/regression test that a large number of AD users are returned by `wbinfo -u`.

Important functions and APIs: uses `ldbsearch` to find `defaultNamingContext`, `ldbmodify` to add/delete users over LDAP, `wbinfo -u`, and `testit_grep_count` from subunit. `NUM_USERS` is fixed at 1234.

Control flow: it generates LDIF add records for `large_ad_0001` through `large_ad_1234` under `CN=Users`, applies them as domain Administrator, then asserts that exactly 1234 lines containing `$DOMAIN/large_ad_` appear in `wbinfo -u`. It then generates matching delete LDIF and removes the users.

State and persistence: creates many users in the AD database and removes them at the end. If the script aborts before deletion, those test users can persist and affect later runs.

Dependencies and integration: depends on an AD DC available via `$DC_SERVER`, administrator credentials, Samba ldb tools, and the `wbinfo` domain enumeration path. It is likely registered or run in AD environments that can tolerate LDAP mutation.

Risks and test signals: no trap ensures cleanup on failure, so mid-run errors can leave users behind. The pass signal is an exact count, which catches paging or enumeration truncation but can be disturbed by stale leftover users from failed runs.
