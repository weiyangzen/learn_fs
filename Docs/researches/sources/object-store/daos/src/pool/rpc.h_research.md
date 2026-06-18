# sources/object-store/daos/src/pool/rpc.h

Purpose: canonical pool RPC protocol definition shared by DAOS pool client and server. It declares operation codes, protocol version behavior, request/reply field sequences, generated RPC types, inline field accessors, and request creation helpers.

Important APIs and types: `POOL_PROTO_CLI_RPC_LIST(ver)` and `POOL_PROTO_SRV_RPC_LIST(ver)` define all client-facing and server/internal pool RPCs and their handlers. `enum pool_operation` derives from those lists. Core field sequences include `DAOS_ISEQ_POOL_OP`/`DAOS_OSEQ_POOL_OP`, create/connect/disconnect/query/query-info, target update/extend/evict/service stop/target disconnect/query, properties, ACLs, list/filter containers, ranks, upgrade, target-query-map, rebuild, self-heal, and recovery-container RPCs. Inline accessors pack/unpack fields such as connect credentials/bulk/version, query bulk/bits, target update arrays, attributes, properties, ACLs, list/filter containers, and request creation.

Control flow: macro lists feed both enum generation and `rpc.c` format arrays, so adding an RPC in one list updates opcode ordering and registration. `pool_req_create_common()` encodes an opcode with module/protocol version, maps endpoint tag through `daos_rpc_tag()`, creates the CRT request, fills UUIDs, optionally assigns client UUID and HLC request time, and returns the request. `dc_pool_req_create()` uses negotiated `dc_pool_proto_version`; `ds_pool_req_create()` obtains the server protocol from `ds_pool_rpc_protocol()`.

State and persistence: declares external `pool_proto_fmt_v6`, `pool_proto_fmt_v7`, and `dc_pool_proto_version`. The header itself defines protocol shape, not runtime storage. Request helpers mutate CRT request input structs and may initialize caller-provided request time.

Dependencies and integration: depends on DAOS RPC macros, rsvc hints, pool maps, pool properties, UUIDs, CRT contexts/endpoints, and server handler symbols referenced by macro lists. It is included by client `cli.c`, protocol implementation `rpc.c`, and server pool handlers.

Risks: any field change requires a DAOS pool protocol version bump and v6/v7 compatibility handling. The RPC input/output structures must avoid compiler-generated padding by construction. Inline accessors assert protocol version `POOL_PROTO_VER_WITH_SVC_OP_KEY` for many client RPCs, so older versions are unsupported on those paths. Macro ordering changes are ABI/protocol-sensitive. `pool_req_create_common()` overwrites endpoint tag with DAOS pool request tag mapping, so callers must pass logical tag values.

Test signals: build-time generation of all `CRT_RPC_DECLARE` types is the first signal. Runtime signals include client protocol negotiation selecting v6 or v7, all `*_in_set_data()`/`*_in_get_data()` round-tripping fields, request creation filling pool UUID/handle/client/time correctly, and server/client format arrays matching `POOL_PROTO_CLI_COUNT` and protocol versions.
