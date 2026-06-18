<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/alpha13/private/phpldapadmin-config.php -->
# sources/user-network-fs/samba/source4/selftest/provisions/alpha13/private/phpldapadmin-config.php

Purpose: phpLDAPadmin configuration fixture customized for an old Samba4 LDAP server.

Important APIs/types/functions: `$ldapservers = new LDAPServers`, `SetValue` calls for server name, LDAPI host URL, session auth type, and DN login attribute.

Control flow: static PHP config initializes one LDAP server entry pointing at the fixture private LDAPI socket path.

State and persistence behavior: no runtime mutation in the Samba tree; consumed as config by phpLDAPadmin if used.

Dependencies and integration points: part of historical provision data, useful for upgrade/dump fidelity.

Risks: absolute LDAPI path is developer-machine-specific. Legacy phpLDAPadmin API may not match current releases.

Test signals: fixture-preservation tests should confirm the file survives dump/undump or upgrade workflows when expected.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/alpha13/private/phpldapadmin-config.php -->
