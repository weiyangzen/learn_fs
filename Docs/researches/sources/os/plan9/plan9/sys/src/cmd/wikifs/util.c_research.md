# File Research: sources/os/plan9/plan9/sys/src/cmd/wikifs/util.c

This file provides general utility helpers for `wikifs`.

Allocation/string:
- `erealloc`, `emalloc`, `estrdup`, and `estrdupn` are fatal allocation helpers with allocation tags.
- `strlower` lowercases ASCII letters in place.

String helpers:
- `s_appendsub` appends a source slice while substituting the earliest matching `Sub.match` with `Sub.sub`.
- `s_appendlist` appends a varargs list of strings to a `String`.

Temporary files:
- `opentemp` copies a template, calls `mktemp`, checks nonexistence, and creates an `ORDWR|ORCLOSE` file up to 10 tries.

Notable risks:
- `opentemp` uses `mktemp`, which is inherently race-prone, though Plan 9 semantics and immediate `create` reduce but do not eliminate concerns.
