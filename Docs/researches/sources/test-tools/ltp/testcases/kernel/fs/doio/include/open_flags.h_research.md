# sources/test-tools/ltp/testcases/kernel/fs/doio/include/open_flags.h

Purpose: `open_flags.h` declares helpers that convert between numeric `open(2)` flag bitmasks and symbolic comma-separated names. The doio tools use these helpers for command-line parsing and diagnostics.

Important APIs and types: `openflags2symbols(int openflags, char *sep, int mode)` formats recognized flag bits into a caller-specified separator style and can append `UNKNOWN` when requested. `parse_open_flags(char *string, char **badname)` parses comma-separated symbols into an `open()` bitmask and reports the location of an invalid token.

Control flow: implementation is external. The documented parser leaves the input string unchanged and returns `-1` on invalid symbols. The formatter recognizes a finite table of known flags that must be updated as platforms add new flags.

State and persistence behavior: no persistent state is declared. Output string ownership is not documented in the header, so callers must inspect the implementation before freeing or reusing returned storage.

Dependencies and integration points: `growfiles.c` uses `parse_open_flags()` for `-o` and `openflags2symbols()` in debug and error messages. `doio.c` has its own local `format_oflags()` instead of using this header.

Risks: platform flag drift can cause valid modern flags to be reported as unknown or rejected. The parser's signal-safety warning notes that a signal during parsing could leave a null byte in the middle of the input string, which implies implementation-level tokenization risk. Lack of const qualifiers makes caller mutation concerns ambiguous.

Test signals: coverage should parse all documented open flags, reject bad tokens with a useful `badname`, format compound masks with several separators, and verify behavior for unknown high bits.
