# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bufmod.h

This header defines the STREAMS buffering module control ABI. It provides `SBIOC*` ioctls to set/get/clear buffering timeout, chunk size, snapshot length, and mode flags.

It defines defaults and mode flags such as send-on-write, no header, no protocol conversion, deferred chunking, and no drops. `struct sb_hdr` is the per-chunk header carrying timestamps, original message length, captured length, and drop count; 32-bit time compatibility types are included.
