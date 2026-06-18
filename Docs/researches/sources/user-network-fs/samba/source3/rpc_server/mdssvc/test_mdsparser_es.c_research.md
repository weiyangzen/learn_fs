# sources/user-network-fs/samba/source3/rpc_server/mdssvc/test_mdsparser_es.c

Purpose: cmocka test program for Spotlight-to-Elasticsearch query mapping used by the mdssvc ES backend.

Important APIs and functions: static `map[]` enumerates expected successful translations for wildcard text search, metadata fields, content-type mappings, dates, numeric fields, path escaping, negation, comparison, boolean operators, and `InRange()`. `map_ignore_failures[]` covers cases where unsupported predicates can be ignored when `elasticsearch:test mapping failures` is enabled. `test_mdsparser_es()` loads the same mapping JSON path used by runtime code and checks `map_spotlight_to_es_query()` output. `main()` initializes Samba command-line/loadparm context, sets log level, parses common options, and runs cmocka with subunit output.

Control flow: the test initializes Samba locale/config, obtains mapping file path from loadparm or datadir default, loads it with Jansson, iterates all required cases with `assert_true()` and `assert_string_equal()`, optionally iterates ignored-failure cases, then decrefs mappings and frees the talloc frame.

State and persistence: test state is local to a talloc stackframe. It reads the installed/source mapping JSON and does not write data.

Dependencies: cmocka, Jansson, Samba cmdline/loadparm/talloc utilities, `es_parser.tab.h`, and the mapper implementation linked into the test binary.

Risks: expected strings are tightly coupled to escaping behavior and mapping JSON contents; legitimate mapping changes require synchronized test updates. Some wide date cases are only compiled on LP64, so 32-bit coverage differs. The optional ignored-failure block is disabled by default unless smb.conf parameters request it.

Test signals: this is the main unit signal for ES query translation. It should be run whenever parser grammar, lexer escaping, mapping JSON, or ES backend query construction changes.
