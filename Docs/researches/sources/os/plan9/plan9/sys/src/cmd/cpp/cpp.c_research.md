# File Research: sources/os/plan9/plan9/sys/src/cmd/cpp/cpp.c

Main driver for the Plan 9 C preprocessor.

It initializes token rows, lexer tables, keyword/macro state, hidesets, and line directives, then repeatedly tokenizes source lines, dispatches `#` control lines, expands macros when possible, suppresses skipped conditional regions, and writes output tokens. `control` implements `#define`, `#undef`, conditionals, `#include`, `#line`, `#error`, `#warning`, `#pragma`, and the extension `#eval`.

The file also provides checked allocation wrappers and formatted diagnostics with source include-stack locations and token/token-row formatting.
