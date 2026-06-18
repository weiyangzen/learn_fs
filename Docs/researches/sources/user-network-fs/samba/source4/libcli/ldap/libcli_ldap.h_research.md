# sources/user-network-fs/samba/source4/libcli/ldap/libcli_ldap.h

Purpose: umbrella LDAP helper header that pulls in LDAP message definitions and selected generated misc types.

Important content: include guard `_SMB_LDAP_H_`; includes `ldap_message.h` and generated `misc.h`; forward declares tevent, credentials, and SID-related structures.

Control flow and state: no executable behavior. It establishes shared type visibility for LDAP client modules.

Dependencies and integration: this is the common include for `ldap_bind.c`, `ldap_client.c`, `ldap_controls.c`, and `ldap_ildap.c`. It bridges generated LDAP message definitions with Samba client code.

Risks: because it includes generated message structures, changes to generated NDR/LDAP definitions propagate broadly. Test signal is compile coverage of LDAP client modules and consumers after interface changes.
