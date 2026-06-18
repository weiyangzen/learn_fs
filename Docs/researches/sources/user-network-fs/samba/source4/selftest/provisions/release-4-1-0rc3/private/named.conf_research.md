<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/release-4-1-0rc3/private/named.conf -->
# sources/user-network-fs/samba/source4/selftest/provisions/release-4-1-0rc3/private/named.conf

Purpose: BIND9 DLZ named configuration fixture from a Samba 4.1.0rc3 provision.

Important APIs/types/functions: DLZ block `AD DNS Zone`, `dlopen` database line for BIND 9.8.0, commented alternative for BIND 9.9.0, and absolute module paths.

Control flow: static BIND include configuring DLZ-backed AD DNS.

State and persistence behavior: configuration fixture only.

Dependencies and integration points: used by DNS/provision upgrade tests to recognize and migrate BIND DLZ-era configuration.

Risks: absolute paths are historical and not portable. Only one database line should be active for the target BIND version.

Test signals: upgrade tooling should preserve or replace BIND DLZ config according to backend migration rules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/release-4-1-0rc3/private/named.conf -->
