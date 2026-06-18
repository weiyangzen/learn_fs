# sources/user-network-fs/impacket/tests/dcerpc/test_epm.py

Purpose: tests RPC Endpoint Mapper lookup and map operations over SMB and TCP.

Important APIs and functions: `EPMTests` binds to `epm.MSRPC_UUID_PORTMAP`. It covers raw `ept_lookup`, helper `hept_lookup`, raw `ept_map`, and helper `hept_map`. It constructs `EPMTower`, `EPMRPCInterface`, `EPMRPCDataRepresentation`, protocol, port, host, and pipe floor structures.

Control flow: lookup retrieves endpoint entries and parses each tower. Helper lookup filters SAMR, ATSVC, and SCMR interface UUIDs. Map constructs a tower for SAMR-like interface data and requests up to four towers. Helper map resolves SMB and TCP bindings for several known interfaces.

State and persistence behavior: read-only endpoint mapper queries.

Dependencies and integration points: depends on endpoint mapper over `\pipe\epmapper` and TCP port 135. It is also indirectly used by `DCERPCTests` mapper-mode subclasses and RAA endpoint discovery.

Risks: endpoint availability depends on Windows version, firewall, and service state. The raw map test builds some unused floor objects and uses fixed UUIDs, so failures can reflect environment rather than Impacket regressions.

Test signals: verifies tower parsing/serialization, endpoint-map helper behavior, and both SMB/TCP EPM transport compatibility across NDR and NDR64.
