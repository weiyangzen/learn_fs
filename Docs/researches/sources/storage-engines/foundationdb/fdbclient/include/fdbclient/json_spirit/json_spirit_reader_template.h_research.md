<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/json_spirit/json_spirit_reader_template.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/json_spirit/json_spirit_reader_template.h

## Purpose
`json_spirit_reader_template.h` implements json_spirit's Boost.Spirit Classic based JSON parser templates for string, stream, iterator, ASCII, and wide-string value types.

## Important APIs, Types, and Functions
Important helpers include `is_eq`, `hex_to_num`, `hex_str_to_char`, `unicode_str_to_char`, `append_esc_char_and_incr_iter`, `substitute_esc_chars`, `get_str`, `Semantic_actions`, `throw_error`, `Json_grammar`, `add_posn_iter_and_read_range_or_throw`, `Multi_pass_iters`, `read_range_or_throw`, `read_range`, `read_string`, `read_string_or_throw`, `read_stream`, and `read_stream_or_throw`.

## Control Flow
Boost.Spirit parses JSON grammar rules for objects, arrays, strings, numbers, booleans, and null. Semantic actions maintain a pointer to the current compound value plus a stack of parent values, adding parsed members to arrays or objects through the value configuration. Non-throwing APIs catch all parse exceptions and return false. Throwing string/stream APIs wrap iterators in position iterators so errors include line and column.

## State and Persistence Behavior
Parsing state is local to `Semantic_actions` and the Boost.Spirit parse invocation. The input stream path disables `skipws` and uses multipass iterators. No database or global state is persisted.

## Dependencies and Integration Points
The header depends on json_spirit value and error headers, Boost.Bind, Boost.Function, Boost version-dependent Spirit Classic includes, multipass and position iterators. It integrates with FoundationDB code that still uses bundled json_spirit for JSON status/config parsing.

## Risks and Edge Cases
The grammar permits C/C++ style comments through the skipper, which is outside strict JSON. Escape handling maps `\uHHHH` directly into the target character type and does not perform surrogate-pair UTF-8 composition. Number parsing tries strict real, signed int64, then uint64. Non-throwing APIs catch all exceptions and lose reason details. Optional `BOOST_SPIRIT_THREADSAFE` is commented out.

## Test Signals
Signals include JSON round-trip tests, invalid JSON error-position tests, comment handling tests, escape and unicode tests, int64/uint64/real parsing tests, stream parsing tests, and wide-string parsing when enabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/json_spirit/json_spirit_reader_template.h -->
