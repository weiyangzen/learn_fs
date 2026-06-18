# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/fcall.h

9P2000 message and stat wire-format interface.

Key contents:
- Defines `Fcall` for all 9P message variants, including version, auth, attach, walk, open/create, read/write, stat/wstat, flush, and error fields.
- Provides little-endian `GBIT*`/`PBIT*` access macros, fixed-size constants, Qid/stat size constants, `NOTAG`, `NOFID`, and `IOHDRSZ`.
- Enumerates 9P message type numbers from `Tversion` through `Rwstat`.
- Declares message/stat conversion routines, formatting helpers, and `read9pmsg()`.

Role in this group:
- Supplies the file protocol representation used by drawterm’s mount/device code and kernel facade.

Notable risks:
- The bit macros are statement-like macros without `do { } while(0)` wrapping, so callers must use them carefully.
