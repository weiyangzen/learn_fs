<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar_tokens.c -->
# `sources/test-tools/filebench/cvars/cvar_tokens.c`

Purpose: Parameter tokenizer and linked-list utilities for CVAR modules.

Important APIs/functions: `tokenize`, `find_token`, `unused_tokens`, `free_tokens`, and private `free_token`. Tokens are `key[:value]` pairs separated by `;` by default.

Control flow: `tokenize` duplicates the parameter string, walks delimiter-separated segments, splits each non-empty segment on the first key/value delimiter, rejects empty keys, allocates token nodes and duplicated key/value strings, links them, and returns the head. `find_token` scans by key and modules mark matches as used. `unused_tokens` finds the first unconsumed token. `free_tokens` releases the list.

State and persistence: token lists are transient allocation-time state and are freed before returning from each CVAR allocation.

Dependencies and integration: uses libc `strdup`, `strchr`, `strlen`, `strcmp`, `malloc`, `free`, and trace logging. Included in every CVAR plugin by `Makefile.am`.

Risks: if `parameters == NULL`, `tokenize` returns success without setting `*list_head`, relying on callers initializing it to NULL. Empty parameter elements are ignored, but empty keys in non-empty elements fail. Duplicate keys are allowed; `find_token` returns the first, leaving later duplicates unused and causing unsupported-parameter failure after module parsing. Memory allocation uses raw `malloc`, not Filebench shared allocator, but tokens are transient.

Test signals: empty string, NULL string, `key:value`, `key`, duplicate keys, trailing semicolon, empty key `:value`, unsupported token detection through `used`, and cleanup under allocation failure.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar_tokens.c -->
