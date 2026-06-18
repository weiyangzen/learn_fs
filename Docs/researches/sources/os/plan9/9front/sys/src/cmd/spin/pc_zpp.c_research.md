# File Research: sources/os/plan9/9front/sys/src/cmd/spin/pc_zpp.c

## Purpose

`pc_zpp.c` is a small built-in preprocessor used only when `PC` is defined. It exists to reduce dependence on an external C preprocessor in the PC version of Spin. The public entry point is `try_zpp(fnm, onm)`, which preprocesses `fnm` into `onm` and returns success; on failure, callers are expected to fall back to a real `cpp`.

## Supported Directives

The directive table supports:

- `#define` for object-like macros without arguments;
- `#undefine`;
- `#ifdef`, `#ifndef`, simple `#if`;
- `#else`, `#endif`;
- `#include` with either `<...>` or `"..."`.

`#if` is intentionally minimal: it accepts literal `0`, literal `1`, or a currently defined macro whose replacement is `0` or `1`. Function-like macros are rejected. Nesting is capped by `MAXNEST` and definitions by `MAXDEF`.

## Macro Handling

`do_define()` trims whitespace, rejects macros with arguments, invalidates earlier definitions of the same name, allocates `src`/`trg` strings, and appends the new definition. `apply()` walks definitions in reverse order and repeatedly substitutes token-bounded occurrences using two generous buffers (`Out1`, `Out2`). It checks for excessive expansion size and prints a circular-expansion warning if the output would exceed `GENEROUS`.

Token boundaries are determined by `isalnum()` and `_`. The implementation is text based and does not parse C expressions beyond simple macro text replacement.

## Conditional and Include Handling

`if_truth[]` stores the truth value for each conditional level and `printing[]` records whether output should be emitted at that level, taking outer levels into account. `do_else()` toggles the current truth value; `do_endif()` decrements nesting and detects underflow. `do_include()` extracts the include target and recursively calls `zpp_do()`.

`process()` identifies directives, emits `#line` information, skips interpretive directives in inactive conditional branches, and returns failure for unknown directives.

## Comment and String State

`in_comment()` maintains a simple lexical state machine with states `PLAIN`, `IN_STRING`, `IN_QUOTE`, `S_COMM`, `COMMENT`, and `E_COMM`. It blanks block-comment contents while preserving line structure, handles quoted strings/chars and backslash escapes, and supports comments spanning input lines.

## Main Processing Flow

`zpp_do()` opens an input file, writes an initial `#line`, reads up to `MAXLINE` chunks, joins backslash-continuation lines, extends reads across unterminated block comments, processes directives, and emits macro-expanded non-directive lines when the current conditional branch is active. `try_zpp()` opens the output file, invokes `zpp_do()`, closes output, and reports success/failure.

## Notable Risks and Behaviors

- The file is completely excluded unless `PC` is defined.
- It is intentionally incomplete and returns failure for unsupported constructs so external `cpp` can be used.
- The directive spelling is `undefine`, not standard `undef`, matching this local implementation.
- Include recursion reuses global macro and conditional state; this is suitable for the simple intended use but not a fully conforming preprocessor.
