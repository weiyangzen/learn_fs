# sources/security-integrity/selinux/libsepol/cil/src/cil_strpool.h

## Purpose

`cil_strpool.h` declares the global string interning API used by CIL parsing and semantic phases.

## Important APIs, Types, and Functions

It includes libsepol `hashtab.h` and declares `cil_strpool_add()`, `cil_strpool_init()`, and `cil_strpool_destroy()`.

## Control Flow and State

Consumers initialize the pool before interning, call `cil_strpool_add()` for canonical pointers, and destroy when done. Returned strings are pool-owned.

## Dependencies, Risks, and Test Signals

Because much CIL code compares interned keys by pointer, callers must not pass non-interned strings where pointer identity is expected. Tests should verify that equal strings return identical pointers and that lifecycle calls bracket all parser/resolver use.
