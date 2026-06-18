# sources/user-network-fs/impacket/impacket/dcerpc/v5/epm.py

## Purpose

`epm.py` implements the DCE/RPC endpoint mapper binding for Impacket. It can query TCP 135, enumerate registered endpoints, map an interface UUID/version to a concrete string binding, and parse or print endpoint mapper tower data.

## Important APIs, Types, And Functions

The module exports `MSRPC_UUID_PORTMAP`, `DCERPCSessionError`, large `KNOWN_UUIDS` and `KNOWN_PROTOCOLS` lookup dictionaries, endpoint lookup/version constants, and floor/protocol identifiers. Tower parsing uses `EPMFloor`, `EPMRPCInterface`, `EPMRPCDataRepresentation`, `EPMProtocolIdentifier`, `EPMPipeName`, `EPMHostName`, `EPMHostAddr`, `EPMPortAddr`, and `EPMTower`.

RPC structures include `RPC_IF_ID`, `ept_lookup_handle_t`, `twr_t`, `twr_p_t`, `octet_string_t`, `prot_and_addr_t`, `protocol_tower_t`, `ept_entry_t`, and tower/entry arrays. RPC calls are `ept_lookup` opnum 2 and `ept_map` opnum 3. Primary helpers are `hept_lookup`, `hept_map`, and `PrintStringBinding`.

## Control Flow

`hept_lookup` optionally creates a TCP transport to `ncacn_ip_tcp:<host>[135]`, binds to the endpoint mapper, and loops `ept_lookup` calls until the returned context handle is null. Each entry is converted into a dictionary with object UUID, annotation bytes, and parsed `EPMTower`.

`hept_map` constructs a protocol tower from the requested interface, data representation, RPC protocol floor, and transport floors for named pipe, TCP, or HTTP. It sets fixed referent IDs for Windows 2003 compatibility, sends `ept_map`, parses the first returned tower, and returns a string binding. `EPMTower.fromString` parses the non-standard tower byte encoding by floor count and floor parser list.

## State And Persistence Behavior

There is no file persistence. Static UUID/protocol dictionaries are in-memory constants. `hept_lookup` accumulates entries locally, while `ept_lookup_handle_t` carries server-side enumeration state between calls. Network connections are closed only when the helper created them.

## Dependencies And Integration Points

Dependencies include `socket`, `struct.unpack`, `six.b`, UUID helpers, DCERPC transport factory, NDR classes, common dtypes, `Structure`, `DCERPCException`, and `LOG`. This is a foundational discovery module used before binding to dynamic RPC services such as DRSR, event log, GKDI, ICPR, and service control interfaces.

## Risks And Edge Cases

Tower parsing is manual and network-driven. Unexpected tower shapes may parse incorrectly or fail. `hept_map` assumes at least one returned tower. Unsupported protocols log and return `None`. Some public constants are misspelled but preserved. `DCERPCSessionError.__init__` assumes a packet with `status`. `PrintStringBinding` has a Python 3 fragility in the unknown-protocol branch using `ord()` on bytes.

## Test Signals

Tests should parse known tower bytes for named pipe, TCP, HTTP, local RPC, NetBIOS, and unknown floors. Fake-DCE tests should verify `hept_lookup` pagination and `hept_map` tower construction, referent IDs, string binding output, unsupported protocols, empty `ITowers`, and malformed tower data.
