# File Research: sources/local-fs/udftools/mkudffs/Makefile.am

Builds the `mkudffs` sbin program.

Sources:
- `main.c`
- `mkudffs.c`
- `defaults.c`
- `file.c`
- `options.c`
- local headers
- shared ECMA/OSTA/libudffs headers

Links against `$(top_builddir)/libudffs/libudffs.la`.

Includes shared headers from `$(top_srcdir)/include`.

Install hooks:
- Creates `mkfs.udf` symlink to `mkudffs` in `sbindir`.
- Removes that symlink on uninstall.

Key role: build and install compatibility glue for the UDF filesystem creation tool.
