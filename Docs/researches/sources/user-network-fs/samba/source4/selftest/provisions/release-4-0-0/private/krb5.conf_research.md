<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/release-4-0-0/private/krb5.conf -->
# sources/user-network-fs/samba/source4/selftest/provisions/release-4-0-0/private/krb5.conf

Purpose: minimal Kerberos configuration fixture for a Samba 4.0.0 release provision.

Important APIs/types/functions: default realm `RELEASE-4-0-0.SAMBA.CORP`, `dns_lookup_realm=false`, and `dns_lookup_kdc=true`.

Control flow: static config used by upgrade/selftest fixtures.

State and persistence behavior: configuration only.

Dependencies and integration points: pairs with release-4-0-0 provision data for upgrade compatibility tests.

Risks: relies on DNS KDC lookup in the test environment.

Test signals: Kerberos client realm selection for release fixture tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/release-4-0-0/private/krb5.conf -->
