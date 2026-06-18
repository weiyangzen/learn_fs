# File Research: sources/os/plan9/9front/sys/src/cmd/cpp/cpp.c

Main control loop for the Plan 9 C preprocessor. It initializes token rows, lexical tables, command-line setup, hidesets, line directives, and then processes token rows until EOF.

Important behavior:
- `process()` reads lines into token rows, routes `#` lines to `control()`, expands macros, suppresses skipped conditional lines, and emits output.
- `control()` implements directives including `define`, `undef`, `include`, conditionals, `line`, `error`, `warning`, `pragma once`, and `eval`.
- Tracks nested `#if` state globally and per include source.
- `#pragma once` stores file identity using qid/type/dev in `incblocked`.
- `error()` formats source stack diagnostics and handles warning/error/fatal severity.
