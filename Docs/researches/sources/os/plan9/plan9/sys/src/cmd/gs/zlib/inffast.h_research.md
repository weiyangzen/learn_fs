# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/inffast.h

## Purpose
Internal declaration header for `inflate_fast()`.

## Contents
Declares:
```c
void inflate_fast OF((z_streamp strm, unsigned start));
```

## Notes
The header warns that applications must not include it directly; public users should include `zlib.h`. It is consumed by `inflate.c` and `infback.c`.
