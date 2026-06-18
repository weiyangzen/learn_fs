# File Research: sources/local-fs/udftools/wrudf/Makefile.am

## Role

Automake definition for the legacy `wrudf` tool.

## Contents

- Builds `wrudf` as a bin program.
- Links against `libudffs`.
- Sources include interactive writer modules, CD-R/CD-RW IO modules, descriptor/command modules, `ide-pc.c`, and UDF headers.
- Adds shared include path.
- If `USE_READLINE` is enabled, links `$(READLINE_LIBS)` and defines `USE_READLINE`.

## Research Notes

The source list shows `ide-pc.c` is a low-level MMC command wrapper used by the higher-level `wrudf` CD writing modules.
