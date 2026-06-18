# sources/user-network-fs/impacket/examples/rpcmap.py

## Purpose

`rpcmap.py` discovers listening MSRPC interfaces for an arbitrary string binding. It first asks the MGMT interface for registered interface IDs, optionally brute-forces known UUIDs, and can further brute-force interface major versions or operation numbers.

## Important APIs, Types, and Functions

`RPCMap` owns a parsed `DCERPCStringBinding`, auth level, brute-force options, UUID database, transport, and DCE object. Key methods are `set_transport_credentials()`, `set_rpc_credentials()`, `set_smb_info()`, `connect()`, `disconnect()`, `do()`, `bruteforce_versions()`, `bruteforce_opnums()`, `bruteforce_uuids()`, and `handle_discovered_tup()`. The CLI uses `parse_identity()` separately for transport and MSRPC credentials.

## Control Flow

The CLI validates options, parses separate auth material for RPC and transport, loads either a single UUID or `rpcdatabase.uuid_database`, creates `RPCMap`, configures credentials and SMB host/port overrides, connects, runs discovery, and disconnects. `do()` binds MGMT and calls `mgmt.hinq_if_ids()`, unless MGMT is unavailable or brute UUID mode is requested. Each found tuple is printed with known protocol/provider metadata and optional version/opnum brute-force results.

## State and Persistence Behavior

The script does not persist local or remote data, but it can generate many RPC connections and calls. `set_rpc_credentials()` enables a lockout-protection flag so access denied on MGMT with credentials does not automatically brute-force unauthenticated paths.

## Dependencies and Integration Points

It depends on Impacket `transport`, `rpcrt`, `epm`, `mgmt`, `uuid`, `rpcdatabase`, `DCERPCStringBinding`, `SMBTransport`, RPC proxy error constants, and `AUTH_BASIC`. It integrates with named-pipe, TCP, HTTP, and RPC-proxy string bindings.

## Risks and Edge Cases

The source TODO notes connections are never fully closed during brute-force loops, because each bind path reconnects on the same DCE object. `elif str(e).find('rpc_s_access_denied')` treats `-1` as truthy, so that condition is broader than intended. Brute opnum mode sends empty calls that can trigger server-side faults or logs. Auth failures and brute forcing may cause lockouts or detection. The printed label has a `Procotol` typo for unknown protocols.

## Test Signals

Mock tests should cover MGMT success, MGMT unavailable fallback, access denied with/without credentials, UUID filtering, version result compaction, opnum result compaction, and SMB transport host/port overrides. Integration tests should include a named-pipe endpoint, an unauthenticated endpoint, authenticated endpoint, and capped brute-force ranges.
