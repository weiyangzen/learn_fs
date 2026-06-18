# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/ECBlockReconstructedInputStream.java

## Purpose
`ECBlockReconstructedInputStream` wraps `ECBlockReconstructedStripeInputStream` to expose normal `InputStream`/`ByteBufferReadable` semantics over reconstructed EC stripes.

## Important APIs and Types
It implements `read(byte[], int, int)`, `read(ByteBuffer)`, `seek`, `getPos`, `getLength`, `getRemaining`, `getBlockID`, `unbuffer`, and `close`. It uses a caller-independent `ByteBuffer[] bufs` of data buffers borrowed from a `ByteBufferPool`.

## Control Flow
Reads allocate one buffer per EC data chunk if needed. `selectNextBuffer` returns the next buffer with remaining data, or calls `readStripe()` to refill all buffers from the stripe reader. `readBufferToDest` copies bytes from selected stripe buffers into the caller buffer and advances logical position. At EOF, it frees buffers to reduce memory. `seek` positions the stripe reader to a stripe boundary, reads that stripe, advances buffer positions within the stripe to the requested offset, and updates `position`.

## State and Persistence Behavior
State is EC config, stripe reader, pooled buffers, byte-buffer pool, closed/unbuffer flags, and logical position. It does not persist data. `freeBuffers` returns borrowed buffers to the pool.

## Dependencies and Integration Points
Created by `ECBlockInputStreamFactoryImpl` when reconstruction is required. It relies on `ECBlockReconstructedStripeInputStream` for actual parallel reads and decoding, and on a `ByteBufferPool` for reusable stripe buffers.

## Risks
The wrapper assumes stripe buffers are returned ready to read. Seek forces a stripe read even if only a small offset is needed, which is expected but can be expensive. `readWithStrategy` is unimplemented, so callers must use byte-array or byte-buffer read paths that this class overrides.

## Test Signals
`TestECBlockReconstructedInputStream` covers normal reads, partial reads, EOF, seek, unbuffer, buffer reuse/freeing, and reconstructed stripe integration.
