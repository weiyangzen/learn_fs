# sources/user-network-fs/samba/source3/rpc_server/mdssvc/es_lexer.l

## Purpose
This Flex lexer tokenizes macOS Spotlight RAW query strings for the mdssvc Elasticsearch backend parser. It recognizes Spotlight comparison operators, boolean operators, quoted phrases, words including UTF-8 sequences, boolean literals, date conversion syntax, and the `InRange` function.

## Important APIs, Types, And Functions
The generated lexer uses the `mdsyyl` prefix and includes `es_parser.tab.h` for token definitions. Token rules return `FUNC_INRANGE`, `DATE_ISO`, `BOOLEAN`, `QUOTE`, parentheses, `AND`, `OR`, equality/inequality and comparison tokens, `COMMA`, `WORD`, and `PHRASE`. `strip_quote()` removes surrounding double quotes from phrase tokens and allocates the result on `talloc_tos()`.

## Control Flow
Flex patterns define ASCII word characters, UTF-8 byte classes, special phrase characters, escaped phrase characters, and blanks. The lexer ignores whitespace, stores semantic values into `mdsyyllval`, and leaves parsing decisions to `es_parser.y`. Phrase matching accepts quoted strings containing word characters, specials, blanks, and escaped `"*` characters.

## State And Persistence
Lexer state is the generated scanner buffer created by `mdsyyl_scan_string()` in the parser. Semantic token strings are transient talloc stack allocations; there is no persistent storage.

## Dependencies And Integration Points
It depends on Samba allocation macros (`SMB_MALLOC`, `SMB_REALLOC`), `talloc_tos()`, generated Bison headers, and the `mdsyyl`-prefixed parser functions. It integrates directly with `map_spotlight_to_es_query()` in `es_parser.y`.

## Risks And Test Signals
Risks include incomplete UTF-8 validation, unrecognized characters causing parse failures, phrase handling that strips quotes but does not unescape every possible sequence, and token precedence interactions with the grammar. Test signals should include ASCII and UTF-8 words, quoted phrases with spaces and escaped quotes/stars, boolean operators, `InRange`, `$time.iso(...)`, unsupported characters, and malformed quotes.
