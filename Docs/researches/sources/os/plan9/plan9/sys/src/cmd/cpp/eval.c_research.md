# File Research: sources/os/plan9/plan9/sys/src/cmd/cpp/eval.c

Evaluator for `#if`, `#elif`, `#ifdef`, and `#ifndef`.

It expands the expression row with `defined` temporarily activated, then uses operator and value stacks to evaluate integer preprocessor expressions with precedence, unary/binary operators, logical short-circuit undefined tracking, ternary `?:`, signed/unsigned comparison handling, shifts, arithmetic, and comma. `tokval` parses numeric constants, character constants including escapes and UTF runes, treats bare names as zero, and reports strings as errors.

Undefined division/modulo and unresolved logical operands are represented with an `UND` value type and produce diagnostics when final expression value is undefined.
