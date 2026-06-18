<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/crackname -->
# sources/user-network-fs/samba/source4/scripting/devel/crackname

Purpose: DRSUAPI development client for exercising `DsCrackNames` against a server.

Important APIs/types/functions: local `do_DsBind`, `drsuapi.drsuapi`, `DsNameRequest1`, name format options, and `misc.GUID`.

Control flow: parses server, credentials, input name, input format, and output format. It refuses anonymous/no-server use, binds to `ncacn_ip_tcp:<server>[seal,print]`, sends one name in `DsCrackNames`, and prints status, result name, and DNS domain.

State and persistence behavior: read-only RPC call with no local persistence.

Dependencies and integration points: integrates with Samba DRS client bindings and is useful for plugfest or replication-debug testing.

Risks: hardcoded default name is a GUID; callers must know DRS name format constants. It assumes sealed TCP DRS is available.

Test signals: returned count/status/result fields from `DsCrackNames`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/crackname -->
