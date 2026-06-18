# sources/storage-engines/sqlite/ext/misc/basexx.c

## Purpose
`basexx.c` combines `base64.c` and `base85.c` into one SQLite extension or shell built-in source, exposing both conversion families from one loadable entry point.

## Important APIs, types, and functions
- `init_api_ptr()` initializes the SQLite extension API pointer once for the combined unit.
- Preprocessor rewrites `SQLITE_EXTENSION_INIT1/2` and entry point names before including `base64.c` and `base85.c`.
- `sqlite3_basexx_init()` calls `BASE64_INIT(db)` and `BASE85_INIT(db)` and returns success only if both registrations succeed.
- `BASEXX_INIT` and `BASEXX_EXPOSE` support shell integration.

## Control flow
At compile time, this file includes both implementation files into one translation unit. At load time, the combined initializer initializes API pointers, registers base64 functions, registers base85 functions, and returns `SQLITE_OK` or `SQLITE_ERROR`.

## State and persistence behavior
It has no runtime state beyond the functions registered by included source files. All per-call conversion state remains in `base64.c` and `base85.c`.

## Dependencies and integration points
It depends directly on the sibling source files `base64.c` and `base85.c`. It is designed for runtime-loadable extension builds and SQLite shell built-in builds using `SQLITE_SHELL_EXTSRC`/`SQLITE_SHELL_EXTFUNCS`.

## Risks and edge cases
- Including C files relies on macro hygiene; future changes to the included files can break combined compilation.
- The success branch calls `BASE64_EXPOSE` twice, likely intending the second call to be `BASE85_EXPOSE`; currently both macros are no-ops, so behavior is unaffected.
- A failure in either component returns generic `SQLITE_ERROR`, losing the specific failing return code.

## Test signals
Load `basexx` and verify `base64`, `base85`, and optionally `is_base85` are available and round-trip values. Build tests should cover both loadable and shell-integrated modes.
