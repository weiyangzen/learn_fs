# File Research: sources/os/plan9/9front/sys/src/cmd/aux/flashfs/mkfs.c

Role: Creates/formats a flashfs image.

Behavior:
- Requires an output file path and accepts `-n nsects`, `-z sectsize`.
- Initializes backend and sector buffer, writes magic headers for generation 0 at sector 0 and generation 1 at the last sector, both with sequence 0.
- Erases every sector in between.

Purpose:
- Produces the initial two-generation empty flashfs layout that `loadfs` expects.
