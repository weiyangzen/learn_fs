# sources/sync-backup/git-lfs/ssh/pktline.go

Purpose: defines the minimal pkt-line interface used by Git LFS SSH transfer and adds optional packet tracing.

Important APIs/types/functions: `pktlineReader`, `Pktline` interface, `TraceablePktline`, `ReadPacketList`, `ReadPacketTextWithLength`, `WritePacket`, `WritePacketText`, `WriteDelim`, and `WriteFlush`.

Control flow: normal `pktline.Pktline` instances are used directly unless `GIT_TRACE_PACKET` is enabled, in which case `TraceablePktline` logs readable packet direction/length and delegates to the underlying pktline implementation. Binary `WritePacket` is intentionally not traced.

State/persistence behavior: no persistence; state is the connection id and underlying pktline pointer.

Dependencies/integration: wraps `github.com/git-lfs/pktline` and `tracerx`. `pktlineReader` bridges response binary data into an `io.Reader`.

Risks: `pktlineReader` type-asserts to either `*pktline.Pktline` or `*TraceablePktline`; any third implementation of `Pktline` would panic. Trace output may include protocol text but avoids binary payloads.

Test signals: packet tracing can be observed under `GIT_TRACE_PACKET`; protocol tests indirectly depend on correct delimiter/flush logging and delegation.
