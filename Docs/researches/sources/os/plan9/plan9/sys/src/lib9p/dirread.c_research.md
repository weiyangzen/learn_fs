# File Research: sources/os/plan9/plan9/sys/src/lib9p/dirread.c

This file provides `dirread9p`, a helper for implementing 9P directory reads from a generator callback.

Key behavior:
- Uses `r->ifcall.offset` and `r->fid->dirindex` to preserve directory iteration position.
- Calls a `Dirgen` callback with a numeric index and caller-provided aux pointer.
- Converts each generated `Dir` to wire format using `convD2M`.
- Stops when the generator ends or the next encoded directory entry will not fit.
- Frees generated `Dir` string fields after each conversion.
- Sets `r->ofcall.count` and updates `fid->dirindex`.

Notable details:
- Offset zero resets iteration to entry zero.
- Nonzero offsets resume from the fid’s saved index rather than deriving an index from byte offset.
