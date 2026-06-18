# sources/user-network-fs/samba/source3/lib/util_tsock.c

## Purpose
`util_tsock.c` provides a generic tevent/tsocket async packet reader that reads an initial amount, asks a caller callback how many more bytes are needed, and repeats until the packet is complete.

## Important APIs and Functions
The public API is `tstream_read_packet_send` and `tstream_read_packet_recv`. `struct tstream_read_packet_state` stores the event context, stream, caller `more` callback, private data, dynamic buffer, and iovec. `tstream_read_packet_done` is the read completion callback.

## Control Flow and State
`send` allocates the state and initial buffer, starts `tstream_readv_send`, and registers the completion callback. On each completion, zero-byte reads are converted to `EPIPE`, errors are propagated, and a null `more` callback means the initial read is the full result. Otherwise the callback receives the current buffer and length and returns `-1` for invalid packet, `0` for complete, or a positive byte count to append. The buffer is grown with talloc and another read is issued.

## Dependencies and Integration Points
It depends on `tevent`, `tstream_context`, `tstream_readv_send/recv`, and Samba Unix error propagation helpers. It is useful for protocols with length-prefixed or self-describing packets layered over tsocket streams.

## Risks and Test Signals
The callback contract is central: a malicious or buggy `more` can request very large allocations, though integer wrap is checked. The helper reads exactly the requested chunks, so packet parsers must avoid underestimating remaining bytes. Tests should cover no-callback reads, multi-stage packet reads, callback `-1`, EOF, underlying stream errors, allocation failure, and size wrap rejection.
