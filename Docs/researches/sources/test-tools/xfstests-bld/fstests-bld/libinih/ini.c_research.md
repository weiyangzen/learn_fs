# sources/test-tools/xfstests-bld/fstests-bld/libinih/ini.c

Purpose: `ini.c` is the vendored inih parser implementation for simple INI-style configuration files.

Important APIs, types, and functions: public functions are `ini_parse_stream()`, `ini_parse_file()`, `ini_parse()`, and `ini_parse_string()`. Internal helpers include `rstrip()`, `lskip()`, `find_chars_or_comment()`, `strncpy0()`, and `ini_reader_string()`. It uses compile-time feature macros from `ini.h` such as `INI_USE_STACK`, `INI_ALLOW_REALLOC`, `INI_ALLOW_INLINE_COMMENTS`, `INI_ALLOW_MULTILINE`, `INI_ALLOW_BOM`, `INI_HANDLER_LINENO`, and allocator options.

Control flow: `ini_parse_stream()` obtains lines from a caller-provided reader, optionally grows the line buffer, strips BOM on first line, trims whitespace, skips comments, handles continuation lines when enabled, parses `[section]` headers, parses `name=value` or `name:value`, strips inline comments and whitespace, and calls the handler callback. It records the first parse or handler error line while optionally continuing. Wrappers adapt `FILE *`, filenames, and strings to the stream parser.

State and persistence: parser state is local: current section, previous name for multiline continuations, line buffer, line number, and first error. It performs no persistent writes. Heap allocation is used only when configured not to use stack buffers.

Dependencies and integration points: paired with `ini.h` and built into `libinih.a`. Consumers supply callbacks that receive transient pointers valid only during the handler call.

Risks: default `MAX_SECTION` and `MAX_NAME` are 50, so long section/name values are truncated. Default `INI_MAX_LINE` is 200, so long lines can be truncated unless heap realloc is enabled. Callback failure semantics depend on macros. Inline comment detection only treats comment prefixes after whitespace. Since handler receives pointers into the mutable line buffer, consumers must copy data if needed.

Test signals: parse files with BOM, comments, inline comments, multiline values, section headers, colon/equal separators, no-value lines under both macro modes, long names/sections/lines, string input, missing file, and handler failure.
