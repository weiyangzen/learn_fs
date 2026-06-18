# sources/user-network-fs/samba/source3/rpc_server/mdssvc/es_mapping.c

## Purpose
This file provides helper functions for translating Spotlight metadata names and type values into escaped Elasticsearch/Lucene query components. It centralizes Lucene and JSON escaping rules and JSON mapping lookup.

## Important APIs, Types, And Functions
`escape_str()` is the internal generic escaping routine. `es_escape_str()` first escapes Lucene special characters, optionally excluding caller-specified characters, then escapes JSON string characters. `es_map_sl_attr()` reads an attribute's `type` and `attribute` from the mapping JSON and returns `struct es_attr_map` with an `ssm_type` and escaped Elasticsearch field name. `es_map_sl_type()` maps Spotlight content type values to MIME type strings.

## Control Flow
Mapping a Spotlight attribute performs two `json_unpack()` calls, searches a static string-to-enum table, allocates an `es_attr_map`, and escapes the target field. Type mapping is a direct JSON lookup. Escaping allocates a worst-case doubled buffer and inserts backslashes for any character in the escape list not present in the exception list.

## State And Persistence
The functions are stateless except for allocations returned under caller-provided talloc contexts and borrowed string pointers from Jansson objects. They do not modify the JSON mapping or persist data.

## Dependencies And Integration Points
The implementation depends on Samba base headers, talloc, Jansson, and `es_mapping.h`. It is called by `es_parser.y` for every parsed attribute, full-text term, string value, date field name, and content type mapping.

## Risks And Test Signals
Risks include returning `false` from a pointer-returning function on allocation failure, JSON schema mismatch, field-name escaping that may not match all Elasticsearch query-string contexts, and caller confusion over exception characters such as `*`, space, backslash, and quotes. Test signals should cover every Lucene special character, JSON quote/backslash escaping, exception behavior, unknown attributes/types, all `ssm_type` strings, and malformed mapping JSON.
