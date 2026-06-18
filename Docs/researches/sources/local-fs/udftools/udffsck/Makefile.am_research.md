# File Research: sources/local-fs/udftools/udffsck/Makefile.am

## Role

Automake definition for a placeholder `udffsck` program.

## Contents

- Builds `udffsck` as `noinst_PROGRAMS`, so it is not installed.
- Uses `main.c`.
- Adds `-I$(top_srcdir)/include`.

## Research Notes

This is not a production fsck tool in this tree; it builds only a local stub.
