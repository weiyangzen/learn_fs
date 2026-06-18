<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/writer.rs -->
## sources/object-store/rustfs/crates/io-core/src/writer.rs

### Purpose
Implements `ZeroCopyObjectWriter`, an in-memory writer optimized around `bytes::BytesMut`/`Bytes` for low-copy object assembly and `tokio::io::AsyncWrite` compatibility.

### Important APIs, Types, And Functions
`ZeroCopyObjectWriter` stores a `BytesMut` buffer, `bytes_written`, and `finalized` flag. Constructors are `new` and `with_capacity`. Write APIs are async `write_zero_copy(Bytes)` and `write_slice(&[u8])`, plus `AsyncWrite::poll_write`. Read/management APIs include `into_bytes`, `as_slice`, `bytes_written`, `capacity`, `len`, `is_empty`, `clear`, and `reserve`. `ZeroCopyWriteError` wraps I/O errors and explicit finalized/invalid-input errors.

### Control Flow
Writes first reject finalized writers, then append data into `BytesMut` and increment `bytes_written`. `into_bytes` consumes the writer, marks it finalized, and freezes the buffer into `Bytes`. The `AsyncWrite` implementation mirrors slice writes and marks finalized on shutdown; flush is a no-op because storage is in memory.

### State And Persistence
All data is held in the process heap until the writer is consumed or cleared. No data is persisted to disk or network. `bytes_written` is reset on `clear`; `finalized` is also reset there.

### Dependencies And Integration Points
Depends on `bytes::{Bytes, BytesMut, BufMut}` and Tokio `AsyncWrite`. Integrates with object write paths needing an in-memory accumulator and with zero-copy metrics in `rustfs-io-metrics`, though no metrics are emitted here.

### Risks
Despite the name, appending a `Bytes` into `BytesMut` via `BufMut::put` may still copy into the mutable buffer; the zero-copy claim depends on bytes crate behavior and source buffer compatibility. The writer is unbounded except by allocation failure; large objects can accumulate whole-object memory. Tests do not directly assert write rejection after `poll_shutdown` on the same writer because `into_bytes` consumes the writer.

### Test Signals
Tokio tests cover construction, `write_zero_copy`, slice writes, conversion to `Bytes`, clear, reserve, multiple writes, `AsyncWriteExt::write`, and debug formatting.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/writer.rs -->
