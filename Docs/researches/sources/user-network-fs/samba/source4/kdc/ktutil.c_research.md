## sources/user-network-fs/samba/source4/kdc/ktutil.c

Purpose: minimal keytab listing utility used for Samba selftests, not a full ktutil replacement.

Important APIs and functions: `main()` requires a single keytab argument, initializes a Samba krb5 context, opens a relative keytab with `smb_krb5_kt_open_relative()`, iterates entries via `krb5_kt_start_seq_get()`/`krb5_kt_next_entry()`/`krb5_kt_end_seq_get()`, unparses principal names, formats enctypes, and prints `principal (enctype)` lines. `smb_krb5_err()` prints krb5 errors, frees the talloc context, and exits.

Control flow: every krb5 operation is fail-fast. If enctype-to-string fails, the numeric enctype is printed instead. Entries are freed after each iteration.

State and persistence: read-only keytab traversal; no keytab modification. Process state is limited to krb5 context, keytab cursor, and talloc allocations.

Dependencies and integration: depends on Samba krb5 wrapper helpers and is likely consumed by test scripts checking generated keytabs.

Risks: exits immediately on cursor close or keytab close errors, which is appropriate for selftest but unsuitable as a robust administrative tool. Output format is intentionally simple and may be depended on by tests.

Test signals: empty keytab, multiple enctypes, unknown enctype fallback, invalid relative path, and resource cleanup under valgrind/asan.
