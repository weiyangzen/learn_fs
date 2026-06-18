# File Research: sources/local-fs/udftools/cdrwtool/Makefile.am

Builds the `cdrwtool` binary.

Sources include local cdrwtool files:
- `main.c`
- `options.c`
- `cdrwtool.c`
- `options.h`
- `cdrwtool.h`

It also directly compiles mkudffs implementation files:
- `../mkudffs/mkudffs.c`
- `../mkudffs/defaults.c`
- `../mkudffs/file.c`

Links against `$(top_builddir)/libudffs/libudffs.la` and includes headers from `$(top_srcdir)/include`.

Key role: makes `cdrwtool` a CD-RW/DVD formatting tool that can also build/write UDF structures by reusing mkudffs internals.
