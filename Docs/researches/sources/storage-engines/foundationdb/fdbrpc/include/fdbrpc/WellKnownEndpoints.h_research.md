## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/WellKnownEndpoints.h

Purpose: Centralizes the reserved well-known endpoint token IDs used by FoundationDB RPC services.

Important APIs/types/functions: `enum WellKnownEndpoints` assigns stable token numbers starting at `WLTOKEN_FIRST_AVAILABLE` for client leader registration, leader election, generation register, protocol info, config transaction/follower services, process endpoint, and reserved count. A static assertion pins `WLTOKEN_PROTOCOL_INFO` to `10`.

Control flow: None at runtime beyond enum use. Request streams call `makeWellKnownEndpoint()` or construct `Endpoint::wellKnown()` with these IDs.

State and persistence behavior: No mutable state. Token values are wire/protocol contracts and must remain unique and stable.

Dependencies and integration points: Depends on `fdbrpc.h` for token definitions. Used by generic hostname actors, leader/config services, and process discovery.

Risks: Reordering or reusing values breaks endpoint compatibility across processes/versions. `WLTOKEN_RESERVED_COUNT` must move only when adding new reserved endpoints.

Test signals: Static assertions/build checks, cross-version endpoint discovery, hostname retry to well-known endpoints, and protocol-info endpoint compatibility.
