# sources/test-tools/ltp/testcases/kernel/fs/doio/include/bytes_by_prefix.h

Purpose: `bytes_by_prefix.h` declares helpers that convert strings with byte-size prefixes into integer byte counts. The doio suite uses this style of helper for command-line size parsing across stress tools.

Important APIs and types: the header declares `bytes_by_prefix(char *)`, `lbytes_by_prefix(char *)`, and `llbytes_by_prefix(char *)`, returning `int`, `long`, and `long long` respectively. There are no structs or constants beyond the `_BYTES_BY_PREFIX_` include guard.

Control flow: no control flow is implemented here. Callers pass a mutable or immutable C string and receive a scaled byte count from the implementation in another source file.

State and persistence behavior: the interface suggests pure conversion with no persistent state. Any overflow behavior depends on the implementation and chosen return width.

Dependencies and integration points: this header is an integration point for utilities that accept human-sized byte arguments. It is independent of doio request structs but fits the same test-tool support layer.

Risks: the prototypes do not use `const char *`, so callers may assume the implementation mutates input. Width-specific return types can overflow silently if the implementation does not validate bounds. The header does not document accepted suffixes, base, or error signaling.

Test signals: coverage should include plain numbers, supported prefix suffixes, invalid suffixes, negative values if allowed, and boundary values for each return type.
