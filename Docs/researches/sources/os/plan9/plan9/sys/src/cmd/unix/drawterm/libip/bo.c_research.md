# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libip/bo.c

Provides host/network byte-order helpers independent of platform endianness.

Key functions:
- Writers: `hnputv`, `hnputl`, `hnputs` for 64-, 32-, and 16-bit big-endian storage.
- Readers: `nhgetv`, `nhgetl`, `nhgets` for big-endian byte arrays.

Important behavior:
- Operates on `uchar*` byte buffers directly and avoids alignment assumptions.
