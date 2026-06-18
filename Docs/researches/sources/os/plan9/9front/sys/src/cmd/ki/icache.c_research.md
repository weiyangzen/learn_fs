# File Research: sources/os/plan9/9front/sys/src/cmd/ki/icache.c

Placeholder instruction-cache hook file for `ki`. `icacheinit` is empty, and `updateicache` only marks its address parameter used. The simulator’s memory fetch path still checks `icache.on` and calls `updateicache`, but this backend does not model cache state or stalls here.

This file exists to satisfy the shared simulator interface declared in `sparc.h` and used by `mem.c`.
