# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifgif.c

`ifgif.c` adds GIF tunnel option status and commands. It reads options with `GIFGOPTS`, prints nonzero flags with names for `NOCLAMP` and `IGNORE_SOURCE`, and writes modified options with `GIFSOPTS`.

Registered commands toggle `noclamp` and `ignore_source` by reading the current option word, setting or clearing the requested bit, and writing it back.
