<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba_upgradedns -->
# sources/user-network-fs/samba/source4/scripting/bin/samba_upgradedns

Purpose: upgrades an older Samba DNS provision to AD-integrated DNS using either `SAMBA_INTERNAL` or `BIND9_DLZ`, optionally migrating records from a flat BIND zone file.

Important APIs/types/functions: `find_bind_gid`, `convert_dns_rdata`, `import_zone_data`, cleanup helpers, `create_dns_partitions`, `fill_dns_data_partitions`, `add_dns_accounts`, `secretsdb_setup_dns`, `create_samdb_copy`, `create_named_conf`, `create_named_txt`, and DNS record classes such as `ARecord`, `SRVRecord`, and `SOARecord`.

Control flow: the command parses `--dns-backend` and `--migrate`, loads provision parameters and LDB handles, validates domain functional level, ensures `DnsAdmins`, optionally parses an existing zone and serial, creates DNS application partitions if missing, fills them automatically or imports zone records, marks the local NTDS DSA as hosting DNS naming contexts, and performs backend-specific setup. BIND9_DLZ creates or repairs dns-HOSTNAME credentials, bind DNS directory contents, keytab links, a SAM DB copy, and configuration files. SAMBA_INTERNAL removes BIND-facing sensitive files/accounts and restores private directory permissions.

State and persistence behavior: mutates samdb, secrets.ldb, DNS application partitions, NTDS naming context attributes, bind DNS directories, keytabs, named configuration files, and old DNS file trees. Cleanup removes obsolete DNS artifacts.

Dependencies and integration points: depends on dnspython zone parsing, Samba provisioning helpers, security SID/NDR packing, system `bind` or `named` group lookup, `smb.conf` server services, BIND DLZ module conventions, and internal DNS service configuration.

Risks: zone migration supports common RR types only; unsupported records are logged and ignored. File cleanup can remove BIND artifacts when switching to internal DNS. Missing IPv4 addresses abort partition creation. Existing partial DNS partitions or backend directories require careful idempotency.

Test signals: logger messages for account creation, partition creation, record import, backend file creation, and final server-services warnings. Post-upgrade tests should query DNS partitions and validate BIND/internal DNS startup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba_upgradedns -->
