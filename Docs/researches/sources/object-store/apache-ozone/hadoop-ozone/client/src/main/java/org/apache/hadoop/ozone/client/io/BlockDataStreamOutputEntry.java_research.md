## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/BlockDataStreamOutputEntry.java

### Purpose
`BlockDataStreamOutputEntry` is a lazy wrapper around `BlockDataStreamOutput` for byte-buffer based key writes. It represents one allocated block stream, tracks position, and exposes retry/cleanup/status helpers used by data-stream output pools.

### Important APIs and Types
Fields include config, lazy `ByteBufferStreamOutput`, block ID, key, xceiver client factory, pipeline, intended length, current position, block token, and shared buffer list. It implements `ByteBufferStreamOutput` methods `write`, `flush`, `hflush`, `hsync`, and `close`. Additional APIs expose closed state, failed servers, written/acknowledged lengths, cleanup, retry writes, builder, and testing getters.

### Control Flow
`checkStream` lazily creates `BlockDataStreamOutput` on first write, cleanup, or retry; preallocated blocks do not open xceiver clients until needed. `write` delegates and increments current position. `close` closes the underlying stream and refreshes `blockID` from the stream so BCSID updates are retained. Ack/written length methods return zero when the stream was never initialized.

### State and Persistence Behavior
The entry tracks local write position and current block ID. Durable block data is written by the underlying `BlockDataStreamOutput` to DataNodes. Closing or ack queries can update the local block ID from the underlying stream.

### Dependencies and Integration Points
It integrates with HDDS `BlockDataStreamOutput`, `ByteBufferStreamOutput`, `StreamBuffer`, `XceiverClientFactory`, `Pipeline`, block tokens, and `BlockDataStreamOutputEntryPool`.

### Risks and Edge Cases
`cleanup` initializes the stream even if no data was written, which may create a client only to clean it up. `write` does not locally bound `len` by remaining capacity; callers must enforce block limits. Shared `bufferList` coordination depends on the pool/stream implementation.

### Test Signals
Tests should verify lazy initialization, position increments, zero ack/written lengths before initialization, block ID refresh on close/ack, hflush-to-hsync behavior, cleanup and retry initialization, and failed-server reporting.
