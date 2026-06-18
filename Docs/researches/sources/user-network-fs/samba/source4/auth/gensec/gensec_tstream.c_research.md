<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/gensec_tstream.c -->
# sources/user-network-fs/samba/source4/auth/gensec/gensec_tstream.c

Purpose: implements a `tstream_context` adapter that transparently wraps and unwraps a plain stream with an established GENSEC security context. It is used after a mechanism has negotiated signing or sealing and exposes normal async `readv`, `writev`, pending-byte, and disconnect operations over protected PDUs.

Important APIs and types: `_gensec_create_tstream()` allocates `struct tstream_gensec`, validates `GENSEC_FEATURE_SIGN` or `GENSEC_FEATURE_SEAL`, records maximum wrap sizes from `gensec_max_input_size()` and `gensec_max_wrapped_size()`, and installs `tstream_gensec_ops`. `struct tstream_gensec` persists the underlying `plain_stream`, `gensec_security`, sticky `errno` value, write limits, and unread unwrapped bytes. Async state types include `tstream_gensec_readv_state`, `tstream_gensec_writev_state`, and a minimal disconnect state.

Control flow: reads first drain any buffered plaintext from `tgss->read.unwrapped`. If callers still need bytes, `tstream_readv_pdu_send()` asks `tstream_gensec_readv_next_vector()` for a 4-byte little-endian length header and then the wrapped blob. The completion path calls `gensec_unwrap()`, steals the plaintext into the stream object, and loops back to fill the caller vectors. Writes copy caller iovecs into chunks no larger than `max_unwrapped_size`, wrap each chunk via `gensec_wrap()`, prefix a 4-byte length using `RSIVAL`, and send header plus blob over the plain stream.

State and persistence: stream failure is sticky through `tgss->error`; future operations immediately complete with that error. Buffered plaintext is kept across reads with offset and remaining-byte counters. Disconnect only detaches the wrapper from the plain stream and marks `ENOTCONN`; the caller still owns the real lower-level disconnect.

Dependencies and integration: depends on Samba talloc, tevent, tsocket/tstream internals, DATA_BLOB helpers, and GENSEC wrap/unwrap APIs. It integrates with higher-level protocols that want a stream abstraction after SPNEGO/Kerberos/NTLMSSP negotiation.

Risks and test signals: the reader rejects zero and extremely large message lengths above `0x0fffffff`, a key fuzz and interoperability boundary. Tests should cover fragmented reads, multi-iovec writes, partial buffered plaintext, wrap failure causing sticky `EIO`, lower-stream errors, signed-only and sealed mechanisms, and disconnect behavior. The header length is the wrapped blob size, so any peer using a different record framing will fail.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/gensec_tstream.c -->
