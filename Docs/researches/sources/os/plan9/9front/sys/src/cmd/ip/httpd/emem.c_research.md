# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/emem.c

Fatal allocation helpers for HTTPD. `ezalloc` allocates and zeroes memory, and `estrdup` duplicates a string; both call `sysfatal("out of memory")` on failure.

Used by other HTTPD support files to keep allocation call sites compact.
