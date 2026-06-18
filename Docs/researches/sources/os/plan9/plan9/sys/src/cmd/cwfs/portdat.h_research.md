# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/portdat.h

Central shared data-layout, constants, type declarations, global state, and device/tag/error enumerations for cwfs.

Key contents:
- Fundamental on-disk constants:
  - `SUPER_ADDR = 2`
  - `ROOT_ADDR = 3`
- Fundamental types:
  - `Wideoff`, `Userid`, `Timet`, `Devsize`.
- Derived layout constants:
  - `BUFSIZE = RBUFSIZE - sizeof(Tag)`
  - `DIRPERBUF`, `INDPERBUF`, `FEPERBUF`
  - message buffer sizes
  - cache bucket sizing constants.
- On-disk structures explicitly marked "DONT TOUCH":
  - `Tag`
  - `Qid9p1`
  - `Super1`
  - `Centry`
  - `Dentry`
  - `Fbuf`
  - `Superb`
  - `Cache`
  - `Bucket`
  - `Label`.
- Runtime structures:
  - `Queue`, `Device`, `Chan`, `Filsys`, `Startsb`, `Time`, `Tlock`, `Cons`, `File`, `Wpath`, `Iobuf`, `Uid`, `Conf`, `Msgbuf`, `Command`, `Flag`, `Rtc`, `Truncstate`, `Map`.
- Enumerations:
  - message categories
  - process states
  - devnone pseudo block numbers
  - internal error codes
  - device types
  - block tags
  - `getbuf` flags.
- Defines global instances `Conf conf; Cons cons;`.
- Vararg format pragmas for `%Z`, `%T`, `%I`, `%E`, `%G`.

Important interactions:
- Included by variant `dat.h` files after block size/address width choices are made.
- `Device` union is the backbone for every storage backend.
- Block tag ordering is important; comments note indirect-tag order is exploited by `indirck()` and `isdirty()`.

Research notes:
- The file is disk-layout critical: changing structures or derived constants changes on-disk compatibility.
- `COMPAT32` changes tag assignments for directory and indirect tags.
- `NDBLOCK`, `NIBLOCK`, `NAMELEN`, and `Off` width are imported from `32bit.h`/`64bit.h`, so this file adapts to multiple build variants.
