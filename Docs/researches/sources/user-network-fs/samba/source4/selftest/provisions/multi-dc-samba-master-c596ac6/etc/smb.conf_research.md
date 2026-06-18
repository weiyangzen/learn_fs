<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/multi-dc-samba-master-c596ac6/etc/smb.conf -->
# sources/user-network-fs/samba/source4/selftest/provisions/multi-dc-samba-master-c596ac6/etc/smb.conf

Purpose: smb.conf fixture for a multi-DC Samba AD provision.

Important APIs/types/functions: `[global]` parameters `workgroup=SAMDOM`, `realm=samdom.example.com`, `netbios name=Q-0-1`, `server role=active directory domain controller`, `log level=3`, plus `netlogon` and `sysvol` shares.

Control flow: static Samba configuration consumed by tests or upgrade fixtures.

State and persistence behavior: configuration only.

Dependencies and integration points: points `netlogon` and `sysvol` at `/usr/local/samba/var/locks/sysvol`, matching the fixture layout expectations.

Risks: absolute paths are fixture-specific. Share writeability is appropriate for AD sysvol tests but not a general hardening example.

Test signals: `testparm` or provision tests should parse it and expose AD DC role plus netlogon/sysvol shares.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/multi-dc-samba-master-c596ac6/etc/smb.conf -->
