# File Research: sources/os/plan9/9front/sys/src/cmd/cpp/eval.c

Evaluator for `#if`, `#elif`, `#ifdef`, and `#ifndef`. It uses a shunting-yard style operator/value stack with Plan 9 `vlong` values and simple signed/unsigned/undefined type tracking.

Important behavior:
- Temporarily activates special `defined` handling before macro expansion.
- Supports arithmetic, relational, shift, logical, unary, comma, and ternary operators.
- Treats ordinary undefined names as zero; `NAME1` from `defined` tests symbol presence.
- Parses decimal/octal/hex integer constants and character constants, including escapes and UTF runes.
- Division/modulo by zero and undefined logical paths propagate an undefined expression state.
