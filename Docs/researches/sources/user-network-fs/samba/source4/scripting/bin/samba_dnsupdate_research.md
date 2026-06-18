<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba_dnsupdate -->
# sources/user-network-fs/samba/source4/scripting/bin/samba_dnsupdate

Purpose: updates the AD DC DNS records listed in `dns_update_list`, using GSS-TSIG `nsupdate`, RPC `samba-tool dns`, or RODC netlogon calls depending on credentials, options, and server role.

Important APIs/types/functions: `dnsobj` parses A, AAAA, SRV, CNAME, NS, and `RPC`-prefixed records; `get_subst_vars` gathers `${DNSDOMAIN}`, `${DNSFOREST}`, `${HOSTNAME}`, `${SITE}`, GUIDs, and role conditionals from `SamDB`; `check_dns_name`, `call_nsupdate`, `call_samba_tool`, `call_rodc_update`, and `rodc_dns_update` implement lookup and update paths. It uses `DNSResolver`, dnspython, `gensec.Security`, `cmd_dns`, `winbind.winbind`, `netlogon`, and KCC site coverage helpers.

Control flow: options and loadparm are parsed, local interface IPs are split into IPv4/IPv6, the update list and cache are read under a file lock, substitutions expand template records, site-specific records are duplicated for uncovered sites, `$IP` records expand across interfaces, and DNS/cache state determines add and delete work. Credentials are obtained only when needed. Deletes run first, then adds, choosing RPC, RODC, or nsupdate per record. The cache is rebuilt atomically when expected records changed.

State and persistence behavior: persists `dns_update_cache` and optionally a test `--use-file` DNS store with `fcntl` locking and temporary-file rename. It creates and later removes a temporary Kerberos ccache and temporary nsupdate command files. Live updates mutate DNS zones through DNS protocol, Samba RPC, or netlogon.

Dependencies and integration points: invoked from Samba AD DC maintenance and installed by the scripting build. It integrates with private `krb5.conf`, `dns_update_list`, `dns_update_cache`, interface configuration, `smb.conf`, internal DNS or BIND DNS, winbind IRPC, and KCC uncovered-site logic.

Risks: DNS update behavior is sensitive to resolver configuration, Kerberos ticket acquisition, stale SOA/NS records, and mixed forest/domain zone layouts. The `--use-file` delete path reparses raw lines and can fail on unexpected entries. RODC mapping only covers selected netlogon DNS names. Failed updates accumulate in `error_count`, so partial DNS state is possible without `--fail-immediately`.

Test signals: selftest can exercise `--use-file`, socket-wrapper environments, DNS update lists, RODC paths, and cache rebuilds. Operational signals are verbose "need update/delete", nsupdate exit codes, samba-tool errors, netlogon status, and rebuilt cache content.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba_dnsupdate -->
