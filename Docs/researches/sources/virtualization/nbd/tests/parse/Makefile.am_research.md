# File Research: sources/virtualization/nbd/tests/parse/Makefile.am

## Purpose
Builds and registers parser tests for `nbdtab` input files.

## Main Contents
- Builds `parser` from `parser.c`.
- Links against `libnbdclt.la` and `libcliserv.la`.
- Runs fixture files through `TESTS_ENVIRONMENT = $(builddir)/parser`.
- Test fixtures are `empty`, `noopts`, `singleopt`, `multiopt`, `ipv6`, and `ipv4`.

## Risks and Notes
The parser executable is used as the test harness for each fixture file.
