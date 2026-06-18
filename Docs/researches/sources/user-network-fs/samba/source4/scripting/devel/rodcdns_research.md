<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/rodcdns -->
# sources/user-network-fs/samba/source4/scripting/devel/rodcdns

Purpose: diagnostic client for the netlogon RODC DNS update IRPC call.

Important APIs/types/functions: `winbind.winbind("irpc:winbind_server")`, `netlogon.NL_DNS_NAME_INFO_ARRAY`, `NL_DNS_NAME_INFO`, and `DsrUpdateReadOnlyServerDnsRecords`.

Control flow: parses weight, priority, port, netlogon DNS type, and site; builds one DNS name info request with `dns_register=True`; calls winbind netlogon with TTL 600; prints returned status.

State and persistence behavior: asks winbind/netlogon to register DNS records for an RODC. No local files are written.

Dependencies and integration points: depends on a running local winbind server and Samba netlogon IRPC implementation.

Risks: numeric record type is user-supplied and defaults to LDAP-at-site. It does not expose unregister mode or detailed returned names.

Test signals: printed status code from `DsrUpdateReadOnlyServerDnsRecords`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/rodcdns -->
