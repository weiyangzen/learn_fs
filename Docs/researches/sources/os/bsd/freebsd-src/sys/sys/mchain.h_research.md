# File Research: sources/os/bsd/freebsd-src/sys/sys/mchain.h

Defines mbuf-chain marshal/unmarshal helper structures and APIs for kernel protocol code.

Key content:
- Kernel-only header.
- Copy modes for `mb_put_mem`/`md_get_mem`: system bcopy, user copyin/copyout, inline copy loop, zero fill, and custom callback.
- `struct mbchain` tracks output chain state: top mbuf, current mbuf, remaining space, byte count, optional custom copy function, and user data.
- `struct mdchain` tracks input parsing state: top mbuf, current mbuf, and current data position.
- Declares builders for padding, integer writes in big/little endian, memory writes, mbuf writes, and UIO writes.
- Declares readers for integer values in native/big/little endian, memory extraction, mbuf extraction, UIO extraction, and record traversal.

Research relevance:
- Common in network filesystem/protocol implementations that serialize request/response fields into mbuf chains.
- Complements `mbuf.h` with a cursor-style API for structured binary protocols.

Cautions:
- Endianness-specific helpers are explicit; callers must choose correctly for protocol wire format.
- Only declarations are here; allocation/failure semantics are implemented elsewhere.
