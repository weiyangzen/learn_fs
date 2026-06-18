# File Research: sources/local-fs/udftools/udflabel/Makefile.am

## Role

Automake definition for `udflabel`.

## Contents

- Builds `udflabel` as an sbin program.
- Links against `libudffs`.
- Sources include local `main.c` and `options.c`, shared `../udfinfo/readdisc.c`, headers, and shared UDF headers.
- Adds include path `-I$(top_srcdir)/include`.

## Research Notes

The shared `readdisc.c` dependency means label updates are based on the same discovery/parser behavior as `udfinfo`.
