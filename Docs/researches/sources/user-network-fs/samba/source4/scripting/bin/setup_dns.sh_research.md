<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/setup_dns.sh -->
# sources/user-network-fs/samba/source4/scripting/bin/setup_dns.sh

Purpose: example helper for setting DNS records after vampiring a domain.

Important APIs/types/functions: shell variables `HOSTNAME`, `DOMAIN`, `IP`, `PRIVATEDIR`, `OBJECTGUID`; tools `samba-tool testparm`, `ldbsearch`, `kinit` or `samba4kinit`, `nsupdate-gss`, `rndc`, and `host`.

Control flow: validates three arguments, uppercases host/domain, derives the DN suffix, discovers private dir when not supplied, looks up the NTDS Settings objectGUID, performs keytab kinit as the machine account, adds the host A record and NTDS GUID CNAME using `nsupdate-gss`, flushes BIND, and checks both names.

State and persistence behavior: writes DNS records to the configured DNS server and uses Kerberos credentials from `secrets.keytab`. It does not edit local DB files directly.

Dependencies and integration points: expects Samba build-tree tools, a matching `PRIVATEDIR`, BIND `rndc`, Kerberos keytab, and the legacy `nsupdate-gss` helper.

Risks: command substitutions are lightly quoted and assume default site paths. It hardcodes `Default-First-Site-Name` and old update tooling. Failure leaves partial DNS state if A succeeds and CNAME fails.

Test signals: visible `host` lookups after `rndc flush` confirm records; failed kinit or nsupdate returns nonzero.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/setup_dns.sh -->
