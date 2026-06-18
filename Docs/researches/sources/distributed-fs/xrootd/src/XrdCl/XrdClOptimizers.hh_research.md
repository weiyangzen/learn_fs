# sources/distributed-fs/xrootd/src/XrdCl/XrdClOptimizers.hh

## Purpose

This header centralizes branch prediction macros used in performance-sensitive XrdCl code.

## Important APIs, Types, And Functions

It defines `likely(x)` and `unlikely(x)`. With GCC they expand to `__builtin_expect(!!(x), 1)` and `__builtin_expect(!!(x), 0)`. On non-GCC compilers they evaluate to `x`.

## Control Flow

Call sites wrap conditions where the common or uncommon path is known. The macros do not change semantics; they only provide compiler hints where supported.

## State And Persistence

There is no state and no persistence.

## Dependencies And Integration Points

The macros are included by logging and other low-level code. They depend only on the `__GNUC__` preprocessor define.

## Risks

Overuse or wrong hints can hurt generated code layout. The non-GCC fallback lacks parentheses around `x`, so unusual expressions can behave differently in macro contexts. Macros live globally after inclusion and can collide with other definitions.

## Test Signals

Build tests on GCC and non-GCC compilers are sufficient. Preprocessor checks should confirm expressions compile in `if(likely(...))` and `if(unlikely(...))` contexts.
