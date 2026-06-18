## sources/user-network-fs/samba/source3/lib/test_tldap.c

Purpose: cmocka test suite for LDAP DN/filter unescape behavior in `tldap.c`, included directly into the test translation unit.

Important tests are `test_tldap_unescape_ldapv3` and `test_tldap_unescape_ldapv2`. Both verify that escaped representations of `(&(objectclass=group)(cn=Samba*))` are decoded in place by `tldap_unescape_inplace`, one using LDAPv3 hex escapes and one using LDAPv2 backslash-literal escaping.

Control flow: each test initializes a mutable `char dn[]`, sets `dnlen = sizeof(dn)`, calls the unescape function, asserts success, and compares the resulting string with the expected unescaped value. `main` registers both tests, selects subunit output, and runs without setup/teardown.

State and persistence: no durable state. The mutation is in-place on stack arrays. Dependencies are cmocka and direct inclusion of `source3/lib/tldap.c`.

Risks: direct implementation inclusion can duplicate compile context and miss integration-link issues. The tests cover successful decode paths only; malformed hex, truncated backslash escapes, embedded NUL, and length-shrinking behavior would be useful additions. These tests are still important signals for LDAP escaping compatibility across LDAPv2 and LDAPv3 forms.
