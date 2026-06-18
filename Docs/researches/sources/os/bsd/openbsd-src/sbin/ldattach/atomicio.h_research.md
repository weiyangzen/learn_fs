# File Research: sources/os/bsd/openbsd-src/sbin/ldattach/atomicio.h

`atomicio.h` declares `atomicio()` and `atomiciov()` and defines `vwrite` as a casted write function pointer compatible with the `atomicio()` signature.

It is a local utility header for reliable complete reads/writes in `ldattach`.
