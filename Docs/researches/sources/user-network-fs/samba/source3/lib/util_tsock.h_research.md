# sources/user-network-fs/samba/source3/lib/util_tsock.h

## Purpose
This header declares the async packet-read helper implemented in `util_tsock.c`.

## Important APIs and Types
It forward-declares `struct tstream_context` and declares `tstream_read_packet_send` plus `tstream_read_packet_recv`. The `more` callback accepts the current buffer, current length, and private data, and returns a signed byte count or error sentinel.

## Dependencies and Integration Points
It includes `replace.h` and `tevent.h`, making it suitable for modules already using Samba async request patterns. Integration is through standard tevent send/recv ownership rules.

## Risks and Test Signals
API risk is callback misuse: callers must keep private data valid until completion and must interpret `perrno` only when recv returns `-1`. Compile tests should verify inclusion without full tsocket internals.
