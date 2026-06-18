# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/emem.c

Fatal allocation wrappers for httpd helpers. `ezalloc` mallocs and zeroes memory, and `estrdup` duplicates strings; both terminate with `sysfatal` on out-of-memory.
