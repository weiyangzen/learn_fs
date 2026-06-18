# File Research: sources/os/plan9/9front/sys/src/cmd/audio/zuke/icy.h

Declaration header for zuke ICY stream support.

Key contents:
- Declares `icyget(Meta *m, int outfd, Channel **newtitle)`.

Role:
- Allows `mkplist.c` and `zuke.c` to share ICY metadata/stream setup.
