# File Research: sources/virtualization/nbd/tests/code/macro.h

## Purpose
Provides a tiny assertion helper used by code tests.

## Main Contents
Defines a static counter and `count_assert(EXPR)`, which prints the incremented assertion number and then calls standard `assert(EXPR)`.

## Risks and Notes
Because it uses `assert()`, tests compiled with `NDEBUG` would not fail on false expressions.
