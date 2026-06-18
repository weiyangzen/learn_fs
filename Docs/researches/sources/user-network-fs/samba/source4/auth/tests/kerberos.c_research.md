# sources/user-network-fs/samba/source4/auth/tests/kerberos.c

Purpose: cmocka tests for Kerberos keytab cleanup, specifically `smb_krb5_remove_obsolete_keytab_entries()`.

Important APIs/functions: `internal_obsolete_keytab_test()` creates an in-memory keytab, adds multiple principals and key version numbers, validates initial ordering, calls the cleanup function, and verifies only the expected previous kvno remains. Public tests cover one principal/two kvnos and many principals/four kvnos.

Control flow: the helper initializes krb5, resolves a `MEMORY:` keytab, constructs principals under `samba.example.com`, inserts entries, iterates to assert order, removes obsolete entries using target `kvno`, then iterates again. Heimdal and MIT memory-keytab order differs, so conditional loops assert the right sequence for each implementation.

State/dependencies/integration: memory keytabs only; no filesystem keytab is modified. Depends on Samba Kerberos utility wrappers, credentials Kerberos headers, cmocka, and platform krb5. It validates service-principal key rotation cleanup.

Risks/test signals: verifies cleanup does not delete the immediately previous kvno needed during rollover. Registered as `test_kerberos` in `auth/wscript_build`.
