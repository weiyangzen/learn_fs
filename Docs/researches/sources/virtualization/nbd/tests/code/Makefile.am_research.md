# File Research: sources/virtualization/nbd/tests/code/Makefile.am

## Purpose
Builds and registers small C tests for server helper functions and refactored client argument parsing.

## Main Contents
- `TESTS` and `check_PROGRAMS` include `clientacl`, `dup`, `mask`, `size`, `trim`, and `args_test`.
- Most helper tests link `libnbdsrv.la`, `libcliserv.la`, and GLib.
- `args_test` compiles `args_test.c` with `../../args.c` and GLib.
- `macro.h` is distributed as shared assertion helper support.

## Risks and Notes
Some tests use `punchdummy.c` or local stubs to satisfy backend symbols and keep the tests focused on helper behavior.
