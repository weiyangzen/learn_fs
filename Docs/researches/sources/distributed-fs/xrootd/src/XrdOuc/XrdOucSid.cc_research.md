# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSid.cc

Purpose: implements a bit-vector stream ID allocator with optional locking and optional overflow delegation to a global `XrdOucSid` pool.

Important APIs, types, and functions: the constructor allocates and initializes `sidVec`; `Obtain()` finds and clears a free bit; `Release()` sets a bit back; `Reset()` marks all local IDs free; the destructor frees the vector.

Control flow: `Obtain()` locks when configured, advances `sidFree` past full bytes, chooses the lowest available bit through a nibble lookup table, clears that bit, and returns the calculated short ID. If the local vector is exhausted and `globalSid` exists, it obtains from the global pool and offsets by `sidMax`. `Release()` reverses this for local IDs or delegates back to the global pool after subtracting `sidMax`.

State and persistence: state is in-memory only: the mutex, local free-bit vector, current free-byte cursor, size/max values, global pool pointer, and lock flag. No IDs persist across object destruction or reset.

Dependencies and integration points: depends on `XrdSysPthread.hh` through the header and libc allocation/string routines in practice. It integrates with connection/session stream management where small integer stream IDs need reuse.

Risks and test signals: the constructor computes `sidSize` as `(numSid / 8) + ((numSid % 8 ? 1 : 0) * 8)`, which adds eight bytes rather than one for non-multiples of eight; this overallocates and changes `sidMax`. `Release()` does not reject negative or duplicate local IDs before setting bits. Tests should cover non-multiple sizes, exhaustion and global fallback, duplicate release, reset, signed short overflow behavior, and MT contention when `mtproof` is true.
