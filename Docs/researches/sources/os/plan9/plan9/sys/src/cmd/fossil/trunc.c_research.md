# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/trunc.c

This is a tiny Plan 9 utility that truncates a file to a requested size. It expects `file size`, initializes a null `Dir`, sets `d.length` from `strtoull`, then applies it with `dirwstat`.

It exits with usage on wrong arity and reports `dirwstat` failures via `sysfatal`.
