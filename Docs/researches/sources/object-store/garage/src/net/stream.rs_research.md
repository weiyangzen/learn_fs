# sources/object-store/garage/src/net/stream.rs

Purpose: common byte stream abstraction used by Garage NetApp message and RPC layers. It converts packetized stream bodies to fixed-size reads and bridges between `ByteStream` and Tokio `AsyncRead`.

Important APIs and types: `ByteStream` is a pinned boxed `Stream<Item = Result<Bytes, io::Error>>`; `Packet` names each stream item. `ByteStreamReader` maintains an internal `BytesBuf`, end-of-stream flag, and deferred stream error. It exposes `read_exact`, `read_exact_or_eos`, `read_u8/u16/u32`, `fill_buffer`, `take_buffer`, `into_stream`, and `eos`. `ReadExactError` separates unexpected EOF from underlying IO failure. `ByteStreamReadExact` implements `Future`.

Control flow: `ByteStreamReadExact::poll` loops until the internal buffer can satisfy the requested byte count, an error arrives, EOF is reached, or the underlying stream yields another packet. `read_exact_or_eos` returns the remaining buffered bytes at EOF, whereas `read_exact` treats early EOF as an error. `into_stream` reconstructs a stream from unread buffered slices, a stored error, and the unconsumed stream tail.

State and persistence: all state is in-memory per reader. The module does not persist data or mutate global state.

Dependencies and integration: uses `bytes::Bytes`, `futures::{Stream, StreamExt, Future}`, Garage `BytesBuf`, and `tokio_util` adapters. `asyncread_stream`, `stream_asyncread`, and `read_stream_to_end` are integration shims for RPC body encoding, client/server connections, and streaming endpoints.

Risks and test signals: subtle behavior centers on preserving packet order and error-as-terminal semantics. `into_stream` must not drop already-read-but-unconsumed buffered bytes. No direct tests in this file; coverage comes through net protocol tests and all RPC streaming paths.
