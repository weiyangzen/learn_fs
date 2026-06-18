# File Research: sources/os/bsd/netbsd-src/lib/libc/regex/Makefile.inc

Build fragment for libc regex sources. It adds `regcomp.c`, `regerror.c`, `regexec.c`, `regfree.c`, and `regsub.c`, sets `.PATH` to the regex directory, defines `POSIX_MISTAKE`, and installs regex manual links.

`POSIX_MISTAKE` affects parser behavior around unmatched `)` in EREs, preserving historical POSIX compatibility noted in `regcomp.c`.
