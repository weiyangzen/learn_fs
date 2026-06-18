# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/plan9.h

Plan 9 platform adapter for bzip2. It includes `<u.h>`, `<libc.h>`, and `<ctype.h>`.

It maps `exit(x)` to Plan 9 `exits((x) ? "whoops" : nil)` and defines `size_t` as `ulong`, giving imported bzip2 code enough compatibility with expected C library names.
