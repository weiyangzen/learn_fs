<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/drs/vampire_ad.sh -->
# sources/user-network-fs/samba/source4/scripting/devel/drs/vampire_ad.sh

Purpose: development workflow to join a Samba DC to an AD domain using vampire/domain-join style setup.

Important APIs/types/functions: sourced `vars`, BIND named template substitution, `rndc reconfig`, `unvampire_ad.sh`, `kinit`, `nsupdate`, and `samba-tool domain join`.

Control flow: creates a named.conf from template, reconfigures BIND, runs cleanup, deletes an existing A record via GSS `nsupdate`, derives uppercase realm, and runs `samba-tool domain join ... DC` with forced ADS function-level options. Old `setup_dns.sh` calls are left commented.

State and persistence behavior: writes named.conf, changes BIND state, deletes DNS records, and creates/updates a local Samba DC provision through domain join.

Dependencies and integration points: depends on DRS test environment variables, administrator password, BIND, Kerberos, and `samba-tool`.

Risks: destructive cleanup runs before join. Password is piped to `kinit` and also appears in command arguments. Hardcoded function-level options target old AD compatibility scenarios.

Test signals: successful `samba-tool domain join`, BIND reconfig, and DNS update completion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/drs/vampire_ad.sh -->
