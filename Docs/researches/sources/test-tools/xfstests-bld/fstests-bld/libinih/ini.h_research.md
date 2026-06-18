# sources/test-tools/xfstests-bld/fstests-bld/libinih/ini.h

Purpose: `ini.h` is the public header for the vendored inih parser, defining callback types, parser entry points, and compile-time configuration macros.

Important APIs, types, and functions: typedefs `ini_handler` and `ini_reader`; functions `ini_parse()`, `ini_parse_file()`, `ini_parse_stream()`, and `ini_parse_string()`. Configuration macros include `INI_HANDLER_LINENO`, `INI_ALLOW_MULTILINE`, `INI_ALLOW_BOM`, `INI_START_COMMENT_PREFIXES`, `INI_ALLOW_INLINE_COMMENTS`, `INI_INLINE_COMMENT_PREFIXES`, `INI_USE_STACK`, `INI_MAX_LINE`, `INI_ALLOW_REALLOC`, `INI_INITIAL_ALLOC`, `INI_STOP_ON_FIRST_ERROR`, `INI_CALL_HANDLER_ON_NEW_SECTION`, `INI_ALLOW_NO_VALUE`, and `INI_CUSTOM_ALLOCATOR`.

Control flow: header-only preprocessor configuration and C++ `extern "C"` wrapping. Macro values selected at compile time alter `ini.c` behavior and callback signatures.

State and persistence: no runtime state in the header. It defines contracts for parser callbacks, including that passed strings are valid only during callback execution.

Dependencies and integration points: included by `ini.c` and by consumers linking against `libinih.a`. Requires `<stdio.h>` for `FILE`.

Risks: changing macros between compiling `ini.c` and compiling consumers can break ABI, especially `INI_HANDLER_LINENO`. Small default line/section/name capacities may surprise consumers. Custom allocator mode requires external functions with exact names/signatures.

Test signals: compile with default macros and with key macro combinations, especially `INI_HANDLER_LINENO`, heap allocation/realloc, no-value support, and C++ inclusion.
