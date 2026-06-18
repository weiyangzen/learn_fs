<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/getncchanges -->
# sources/user-network-fs/samba/source4/scripting/devel/getncchanges

Purpose: command-line DRS replication diagnostic for issuing `DsGetNCChanges` requests against a server.

Important APIs/types/functions: `drs_DsBind`, `DsGetNCChangesRequest8`, `drs_get_rodc_partial_attribute_set`, replica flag options, `SamDB`, `ndr_unpack(misc.GUID)`, and high-watermark update loop.

Control flow: parses server, credentials, naming context DN, extended operation, partial attribute set, iteration count, destination DSA, and replica flags. It adjusts flags for RODC or partial RW modes, connects to DRS over sealed TCP, opens remote LDAP, discovers destination DSA invocation ID if absent, builds a request8 from zero high-watermark, optionally adds the RODC PAS, calls `DsGetNCChanges` repeatedly while `more_data` is set, and feeds back the returned high-watermark.

State and persistence behavior: read-only replication pull from the target, with no local writes.

Dependencies and integration points: exercises Samba DRS server behavior, LDAP metadata discovery, and partial attribute set generation.

Risks: uses `opts.dn.decode("utf-8")`, which is Python 2-era and problematic when `opts.dn` is already `str`. Incorrect flags can ask for secret-processing or partial replicas unexpectedly. Output is minimal, so failures may need DRS tracing.

Test signals: DRS bind handle, successful iterations, `more_data` termination, and absence of RPC exceptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/getncchanges -->
