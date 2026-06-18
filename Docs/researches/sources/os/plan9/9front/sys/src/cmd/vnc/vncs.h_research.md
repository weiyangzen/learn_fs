# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/vncs.h

## Role

`vncs.h` declares VNC server-side session and dirty-region structures plus encoder entry points.

## Main Definitions

- `Rlist`: dirty rectangle list with bounding box, capacity, count, and rectangle storage.
- `Vncs`: embeds `Vnc` and adds client list linkage, remote/net path strings, encoding callbacks, copyrect/warp/resize flags, update request counter, dirty region list, process lifecycle counters, cursor/snarf tracking, and per-client converted framebuffer image.

## Declared Functions

- RRE/raw/hextile/CoRRE count and send functions from `rre.c`.
- `addtorlist()` and `freerlist()` from `rlist.c`.

## Notable Limitations And Risk Areas

- `Vncs` is shared between multiple rforked processes for one client, so fields like `ndead`, `nproc`, and update state depend on locking discipline.
- Encoder callbacks must keep count/send results consistent; `vncs.c` disconnects the client if counts mismatch.
