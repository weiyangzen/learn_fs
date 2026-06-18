# sources/user-network-fs/samba/source3/rpc_server/mdssvc/es_parser.y

## Purpose
This Bison grammar converts macOS Spotlight RAW query syntax into Elasticsearch query-string syntax. It supports boolean composition, comparisons, date normalization, range functions, content type expansion, full-text terms, and configurable handling for unknown mappings.

## Important APIs, Types, And Functions
The exported API is `map_spotlight_to_es_query(TALLOC_CTX *, json_t *, const char *, char **)`. Parser state is held in `struct es_parser_state`, including a talloc stack frame, JSON mapping objects, config flags, scanner buffer, type-error flag, and final result. Helper functions include `isodate_to_sldate()`, `map_type()`, `map_num()`, `map_fts()`, `map_str()`, `map_sldate_to_esdate()`, `map_date()`, and `map_expr()`. The grammar uses tokens from `es_lexer.l` and returns strings as semantic values.

## Control Flow
`map_spotlight_to_es_query()` extracts `attribute_mappings` and `mime_mappings`, creates a scanner over the query string, reads Samba `elasticsearch:*` options, sets the global parser state, and calls `mdsyylparse()`. Grammar rules reduce parenthesized expressions, `&&`, `||`, comparisons, `InRange(attribute,start,end)`, and `$time.iso(...)` values. Attribute reductions call `es_map_sl_attr()` and abort unless unknown attributes are configured to be ignored. Expression mapping dispatches on `ssm_type`, generating Lucene fragments such as field equality, negative clauses, open/closed numeric/date ranges, full-text terms, and MIME type lists.

## State And Persistence
Parser state is per call but stored in a global pointer while parsing because generated lexer/parser functions need shared state. Temporary strings live on a talloc stack frame and the final query is copied to the caller's context. The parser reads loadparm booleans but writes no persistent state.

## Dependencies And Integration Points
The grammar depends on generated Flex/Bison code, Jansson, Samba loadparm, `mdssvc_es.h`, `es_mapping.h`, `smb_strtox`, and time conversion functions. It is the main query translation layer used by the mdssvc Elasticsearch backend and by `es_parser_test.c`.

## Risks And Test Signals
Risks include the global parser state making concurrent parses unsafe unless serialized, limited grammar coverage for Spotlight syntax, `%expect 1` indicating a known parser conflict, substring forcing changing query semantics broadly, date conversion edge cases around invalid input and time ranges, and ignored unknown attributes producing partial queries. Test signals should cover operator precedence, nested parentheses, AND/OR with ignored subexpressions, numeric/string/date/type/full-text mappings, `InRange`, `$time.iso` conversion both directions, config toggles for unknown attributes/types and substring search, malformed syntax, and concurrent-call assumptions.
