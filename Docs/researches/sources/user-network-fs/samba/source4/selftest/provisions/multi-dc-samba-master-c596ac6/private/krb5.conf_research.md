<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/multi-dc-samba-master-c596ac6/private/krb5.conf -->
# sources/user-network-fs/samba/source4/selftest/provisions/multi-dc-samba-master-c596ac6/private/krb5.conf

Purpose: minimal Kerberos fixture for the multi-DC `SAMDOM.EXAMPLE.COM` provision.

Important APIs/types/functions: `[libdefaults]`, `default_realm`, `dns_lookup_realm=false`, and `dns_lookup_kdc=true`.

Control flow: static Kerberos client defaults for tests.

State and persistence behavior: configuration only.

Dependencies and integration points: consumed by Samba/Kerberos commands in historical provision tests.

Risks: DNS KDC lookup means tests need suitable DNS or socket-wrapper setup.

Test signals: Kerberos tools should select `SAMDOM.EXAMPLE.COM` as default realm.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/multi-dc-samba-master-c596ac6/private/krb5.conf -->
