# sources/user-network-fs/samba/source4/wrepl_server/wrepl_server.h

Source read signal: reviewed complete local file (321 lines, 8056 bytes).

## Purpose
`wrepl_server.h` is the shared private interface for Samba's WINS Replication server. It defines the service-wide state object, incoming/outgoing connection state, partner configuration/runtime state, WINS owner table entries, default timing constants, association-context constants, and includes the generated WREPL server prototypes used across the implementation files.

## Important APIs, types, and functions
Important declarations are `WREPLSRV_VALID_ASSOC_CTX`, `WREPLSRV_INVALID_ASSOC_CTX`, `enum winsrepl_partner_type`, `WINSREPL_DEFAULT_PULL_INTERVAL`, `WINSREPL_DEFAULT_PULL_RETRY_INTERVAL`, and `WINSREPL_DEFAULT_PUSH_CHANGE_COUNT`. Core structs are `wreplsrv_in_call`, `wreplsrv_in_connection`, `wreplsrv_out_connection`, `wreplsrv_partner`, `wreplsrv_owner`, and `wreplsrv_service`. The header pulls in `wrepl_out_helpers.h` and generated `wrepl_server_proto.h`, making it the module boundary for other WREPL server source files.

## Control flow
There is no executable control flow in the header, but it encodes lifecycle relationships. A `wreplsrv_service` belongs to one `task_server` and owns database handles, connection lists, partner lists, owner tables, periodic timers, and scavenging state. Incoming calls attach to an inbound connection and carry parsed request/reply packets plus input/output blobs. Outgoing connections attach to a partner and hold a WREPL socket plus association-context negotiation state. Pull and push substructures inside each partner record hold timers, retry/error counters, current composite requests, and per-cycle IO state.

## State and persistence
All structs are in-memory task state, normally talloc-owned by the service or connection. Persistent database handles are referenced through `wins_db` and `config.ldb`; timers and outstanding requests are transient tevent/composite state. Partner state records the configured address/name/source address, type, pull intervals, retry status, push max-version sent to the partner, and whether push notifications use inform messages. Owner state mirrors WREPL owner/version rows and links owners back to configured partners when possible.

## Dependencies and integration points
The header depends on Samba network types, WINS replication generated packet structs, stream/tstream/tevent/composite abstractions, WINS database handles, and helper headers. It is consumed by the WREPL inbound call/connection, outbound helper/pull/push, periodic, scavenging, and server bootstrap code.

## Risks
Because this is a shared private header, layout changes affect many modules at once. Association context constants must remain synchronized with protocol handling. Pull and push nested state mixes configuration, last error state, timer handles, and active composite requests; ownership or cancellation changes need careful review. The header lacks include guards in this snapshot and relies on normal project include behavior.

## Test signals
Build coverage of all WREPL server modules is the primary signal. Runtime tests should observe that partner timers, push notifications, association contexts, inbound connection shutdown, and owner-table updates still operate after any struct or constant change.
