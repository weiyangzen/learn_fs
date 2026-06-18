# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/msgdb.h

- Role: Abstract interface for a message token database.
- Key API: `mdopen`, `mdget`, `mdput`, `mdenum`, `mdnext`, and `mdclose`.
- Integration: Used by `msgdb.c` and `msgclass.c`; implemented by `msgdbx.c`.
