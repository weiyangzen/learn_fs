# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/pc_zpp.c

This is a small built-in preprocessor used only under `#ifdef PC`, intended to reduce dependence on an external C preprocessor in the PC version of Spin.

Supported preprocessor features:
- Object-like `#define` without arguments.
- `#undefine`.
- `#ifdef`, `#ifndef`, simple `#if 0`/`#if 1` or matching defined-symbol values.
- `#else`, `#endif`.
- `#include` with quoted or angle-bracket filenames.
- `#line` and numeric line directives.
- `#error` and `#warning`.

Major functions:
- `try_zpp(fnm, onm)` opens the output and runs `zpp_do`.
- `zpp_do()` reads the input file, handles line continuations, strips comments, applies directives, emits `#line` markers, and writes macro-expanded lines.
- `process()` dispatches directive names to handler functions.
- `do_define()` stores simple macro mappings in a fixed `MAXDEF` table.
- `apply()` repeatedly expands known macros using two static output buffers.
- `in_comment()` implements a small lexer state machine that tracks strings, character quotes, and C comments.
- `strip_cpp_comments()` removes `//` comments, with a simple escaped-slash check.

Limits and fallback behavior:
- `MAXNEST` is 32 conditional levels.
- `MAXDEF` is 128 defines.
- `MAXLINE` is 2048 and macro expansion uses 8192-byte buffers.
- Function-like macros are not supported; encountering one returns failure so Spin can fall back to an external `cpp`.
- Complex `#if` expressions are unsupported unless reducible to `0` or `1`.

Risk notes:
- `apply()` has a questionable boundary test around `in2+j == '\0'`; `in2+j` is a pointer, so this condition does not test the character value. The intended check is likely `*(in2+j) == '\0'`.
- Include handling recursively calls `zpp_do` but does not manage include search paths.
- Macro expansion is intentionally lightweight and not a full C preprocessor.
