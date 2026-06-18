<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/release-4-1-6-partial-object/private/krb5.conf -->
# sources/user-network-fs/samba/source4/selftest/provisions/release-4-1-6-partial-object/private/krb5.conf

Purpose: minimal Kerberos configuration fixture for a Samba 4.1.6 partial-object provision.

Important APIs/types/functions: default realm `SAMBA.EXAMPLE.COM`, `dns_lookup_realm=false`, and `dns_lookup_kdc=true`.

Control flow: static Kerberos defaults.

State and persistence behavior: configuration only.

Dependencies and integration points: accompanies the partial-object historical provision fixture.

Risks: DNS KDC lookup dependency must be provided by tests.

Test signals: Kerberos commands should use `SAMBA.EXAMPLE.COM` by default.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/release-4-1-6-partial-object/private/krb5.conf -->
