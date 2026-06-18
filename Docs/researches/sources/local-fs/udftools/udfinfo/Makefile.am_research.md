# File Research: sources/local-fs/udftools/udfinfo/Makefile.am

## Role

Automake definition for the `udfinfo` utility.

## Contents

- Builds `udfinfo` as a bin program.
- Links against `$(top_builddir)/libudffs/libudffs.la`.
- Sources include `main.c`, `readdisc.c`, option/reader headers, and shared UDF headers.
- Adds include path `-I$(top_srcdir)/include`.

## Research Notes

`readdisc.c` is shared with `udflabel`, making `udfinfo` the read-only frontend over the shared parser.
