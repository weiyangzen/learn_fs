# sources/storage-engines/wiredtiger/test/csuite/random_directio/util.h

Purpose: small header exposing the direct-I/O directory copy helper used by `random_directio/main.c`.

Important APIs, types, and functions: contains `#pragma once` and the declaration `extern void copy_directory(const char *, const char *, bool);`.

Control flow: no executable control flow; it provides the function prototype so the main test can call the helper implemented in `util.c`.

State and persistence behavior: no state is stored in the header. The declared function writes destination directory trees at runtime.

Dependencies and integration points: included by both `main.c` and `util.c`; requires `bool` to be available from included headers in those translation units. CMake must compile `util.c` with the main source for the symbol to resolve.

Risks: the declaration lacks parameter names and documentation beyond the file comment, so callers must refer to `util.c` for argument meaning. Any signature change must be synchronized with `main.c` and `util.c`.

Test signals: successful compilation/link of `test_random_directio` and runtime direct-I/O copy cycles confirm the header and implementation stay aligned.
