# sources/object-store/daos/src/pool/rpc.c

Purpose: implementation of pool RPC protocol serialization formats and common pool RPC helper routines shared by client and server pool code.

Important APIs and functions: `dc_pool_op_str()` maps pool operation enums to strings. Custom CRT processors serialize `struct pool_target_addr`, `struct rsvc_hint`, and `daos_pool_cont_filter_t` parts. `CRT_RPC_DEFINE()` instantiates all pool RPC formats. `pool_proto_fmt_v6` and `pool_proto_fmt_v7` expose protocol format tables. Helper functions include `pool_query_bits()`, `pool_query_reply_to_info()`, `list_cont_bulk_create()`, `list_cont_bulk_destroy()`, `map_bulk_create()`, and `map_bulk_destroy()`.

Control flow: RPC format arrays are generated from `POOL_PROTO_CLI_RPC_LIST()` and `POOL_PROTO_SRV_RPC_LIST()` macros. Filter serialization allocates nested filter-part arrays while decoding and frees partial allocations on failure or during FREEING. `pool_query_bits()` maps requested `daos_pool_info_t` bits and property entries into server query-bit flags. Bulk helpers allocate/register pool map or container buffers with CRT and clean both CRT bulk and local buffers.

State and persistence: global protocol descriptors are static/global process state. Bulk helper allocations are per call. No durable state is changed directly.

Dependencies and integration: depends on DAOS RPC/CART, pool map buffers, property definitions, rsvc hints, and `rpc.h` macro declarations. It is the serialization backbone for `cli.c` and server pool handlers.

Risks: protocol list ordering must remain consistent with `enum pool_operation` and registered handler arrays. `pool_query_bits()` intentionally falls through from `DAOS_PROP_PO_REDUN_FAC` to include `DAOS_PROP_PO_EC_PDA`; this must be deliberate or documented because it broadens queries. Filter-part decode must free nested allocations on all failures to avoid leaks. `map_bulk_destroy()` assumes a valid bulk handle, unlike `list_cont_bulk_destroy()` which tolerates `CRT_BULK_NULL`.

Test signals: protocol registration should succeed for v6/v7, op string mapping should return enum names, query-bit tests should verify every property flag, and serialization tests should cover filter decoding/freeing and bulk helper cleanup on CRT failures.
