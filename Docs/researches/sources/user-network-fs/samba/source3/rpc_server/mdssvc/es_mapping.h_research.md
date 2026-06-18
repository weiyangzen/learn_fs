# sources/user-network-fs/samba/source3/rpc_server/mdssvc/es_mapping.h

## Purpose
This header defines the public mapping API used by the mdssvc Elasticsearch query parser. It describes the small type system for mapped Spotlight attributes and declares escaping and lookup helpers.

## Important APIs, Types, And Functions
`enum ssm_type` classifies mapped attributes as boolean, numeric, string, full-text string, date, or special content type. `struct es_attr_map` pairs that type with an escaped Elasticsearch field name. The public functions are `es_escape_str()`, `es_map_sl_attr()`, and `es_map_sl_type()`.

## Control Flow
Callers load mapping JSON, pass the `attribute_mappings` object to `es_map_sl_attr()`, and dispatch on `es_attr_map.type` to build query expressions. For `ssmt_type`, callers pass the `mime_mappings` object to `es_map_sl_type()`.

## State And Persistence
The header defines no state. Returned `es_attr_map` objects and escaped strings are owned by caller-provided talloc contexts, while MIME type strings are borrowed from Jansson-managed JSON.

## Dependencies And Integration Points
It includes Jansson and relies on `TALLOC_CTX` from surrounding Samba headers. It is included by `es_mapping.c`, `es_parser.y`, and the standalone parser test program.

## Risks And Test Signals
Risks are ABI/API coupling to the JSON schema and the parser's switch over `enum ssm_type`. Adding a new mapping type requires changes in both this header and parser mapping logic. Test signals are compile tests for users of the header, query generation for each enum value, and checks that borrowed JSON strings are not used after `json_decref()`.
