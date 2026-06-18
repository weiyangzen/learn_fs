<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/alpha13/private/krb5.conf -->
# sources/user-network-fs/samba/source4/selftest/provisions/alpha13/private/krb5.conf

Purpose: Kerberos configuration fixture for an old `alpha13.samba.corp` provision.

Important APIs/types/functions: `[libdefaults]`, realm `ALPHA13.SAMBA.CORP`, KDC/admin server host `ares.alpha13.samba.corp`, and `[domain_realm]` mappings.

Control flow: static config directs Kerberos clients to use DNS lookup and the explicit realm host mappings.

State and persistence behavior: no code; consumed as configuration by tests or upgrade fixtures.

Dependencies and integration points: part of selftest historical provision data used by upgrade/dump tests.

Risks: hardcoded hostnames are fixture values and should not be used as live config. DNS lookup settings can mask missing explicit KDCs.

Test signals: Kerberos tools using this fixture should resolve the default realm and host mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/alpha13/private/krb5.conf -->
