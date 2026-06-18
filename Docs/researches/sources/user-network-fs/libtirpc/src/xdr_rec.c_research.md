# sources/user-network-fs/libtirpc/src/xdr_rec.c

Purpose: `xdr_rec.c` implements the ONC RPC record-marking XDR backend used over byte streams such as TCP.

Important APIs, types, and functions: Public routines are `xdrrec_create`, `xdrrec_skiprecord`, `xdrrec_eof`, `xdrrec_endofrecord`, `__xdrrec_getrec`, and `__xdrrec_setnonblock`. Internal `RECSTREAM` tracks input/output buffers, current fragment header, last-fragment state, read/write callbacks, nonblocking header/record accumulation, and maximum record limits.

Control flow: Creation allocates send and receive buffers, installs `xdrrec_ops`, reserves space for an outgoing fragment header, and initializes input as empty. Encode operations append XDR units/bytes to the output buffer and flush fragments when full. `xdrrec_endofrecord` marks the fragment with `LAST_FRAG` and either flushes or starts another buffered record. Blocking decode reads fragment headers through `set_input_fragment`, consumes bytes from input buffers, and skips leftover fragments before a new record. Nonblocking decode uses `__xdrrec_getrec` to accumulate a full record, validate fragment lengths against `in_maxrec`, resize the buffer if needed, and expose the complete record to XDR decoders.

State and persistence behavior: Stream state is heap-allocated and owned by the `XDR` object until `xdrrec_destroy`. It persists buffered output between batched calls and buffered/partial input between reads. No durable persistence exists.

Dependencies and integration points: It depends on caller-provided read/write functions, RPC service/client transport status enums, `rpc/xdr.h`, and memory allocation macros. `svc_vc.c` uses it for server-side TCP streams, and client connection-oriented transports use the same record layer.

Risks: Blocking mode only rejects zero-length fragment headers; huge fragment sizes can still drive long reads unless transport-level limits exist. Nonblocking mode rejects zero, over-`maxrec`, and cumulative over-`maxrec` fragments, but `realloc_stream` failure is ignored by `__xdrrec_getrec`, leaving potential decode failure or memory pressure behavior. Pointer arithmetic casts through integer types in several places. `xdrrec_getpos` decode position semantics are unusual and should not be treated as an absolute stream offset.

Test signals: Tests should cover multi-fragment records, batched records, blocking EOF/skip behavior, nonblocking partial headers and payloads, max-record rejection, realloc growth, write callback short writes, and XPRT status transitions.
