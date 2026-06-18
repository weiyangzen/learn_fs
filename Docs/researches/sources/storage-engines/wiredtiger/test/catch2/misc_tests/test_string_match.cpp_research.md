# Research: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_string_match.cpp

## sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_string_match.cpp

Purpose: Unit tests for string/config matching macros: `WT_STRING_LIT_MATCH`, `WT_CONFIG_LIT_MATCH`, `WT_STRING_MATCH`, and `WT_CONFIG_MATCH`.

Important APIs/types: uses `WT_CONFIG_ITEM` with explicit `str` and `len` to verify length-aware matching, including inputs that are not necessarily null-terminated. Literal macros require literal left operands; generic macros support variables.

Control flow: the test creates a `green` config item (`"green"`, length 5), an empty config item, literal/variable strings, and a guarded null pointer. Each section loops twice: first with `green.str` exactly `"green"`, then with `"greenery"` while retaining `green.len == 5`, proving comparisons honor the supplied length rather than C string termination. It checks shorter, longer, different, empty, and null-plus-zero-length cases.

State and persistence: no persistent state. The only mutation is changing `green.str` between loop iterations.

Dependencies/integration: depends on macro definitions in `wt_internal.h` and compiler behavior around literal macros. Risks include misuse of literal macros with non-literals, intentionally noted in comments. Test signals are boolean macro results for literal and variable paths.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_string_match.cpp -->
