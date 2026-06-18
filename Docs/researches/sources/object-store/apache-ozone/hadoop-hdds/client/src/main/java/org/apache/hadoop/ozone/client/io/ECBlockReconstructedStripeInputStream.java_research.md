# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/ECBlockReconstructedStripeInputStream.java

## Purpose
`ECBlockReconstructedStripeInputStream` reads full EC stripes when some data blocks are missing or marked bad. It can either reconstruct missing data chunks for client reads or recover specified data/parity chunks for offline recovery.

## Important APIs and Types
Main public APIs are `readStripe(ByteBuffer[])`, `recoverChunks(ByteBuffer[])`, `setRecoveryIndexes(Collection<Integer>)`, `addFailedDatanodes(Collection<DatanodeDetails>)`, `getFailedIndexes()`, `seek(long)`, `unbuffer`, and `close`. Important internal state includes decoder input/output buffers, missing/data/padding/parity index sets, selected indexes, internal buffer indexes, failed data indexes, byte-buffer pool, `RawErasureDecoder`, executor, and recovery indexes.

## Control Flow
Before the first read, `init()` creates the decoder, marks missing locations as failed, selects indexes, verifies sufficient locations, and allocates internal buffers. `read` validates caller buffers, assigns them to decoder inputs or outputs, clears internal buffers, sets limits for partial final stripes, and loads selected indexes in parallel using the executor. Failed reads mark indexes failed, seek back to the current stripe, reset caller buffers, and reinitialize with new selections. If indexes are missing, it pads short final-stripe buffers, flips inputs, decodes erased indexes into output buffers, and resets limits. Without missing indexes, it flips direct input buffers. Position advances by bytes in the stripe.

## State and Persistence Behavior
State is in-memory reconstruction working set. Internal buffers are borrowed from and returned to the `ByteBufferPool`. It does not persist data; it reads surviving data/parity internal blocks and reconstructs bytes in memory. At logical EOF it frees internal buffers and closes underlying streams without marking the reader closed.

## Dependencies and Integration Points
Extends `ECBlockInputStream` to reuse EC location handling and internal stream opening. It integrates with `RawErasureDecoder` from Ozone erasure-code utilities, `CodecUtil`, executor futures, `ByteBufferPool`, and `BadDataLocationException`.

## Risks
This is the highest-complexity reader in the subset. Index selection must choose enough data/padding/parity inputs and avoid failed/recovery indexes. Partial final stripes require precise limit and zero-padding behavior or decode output may contain garbage. Parallel reads rely on lower-level client timeouts; futures are waited without an additional timeout. `seek` only accepts stripe-aligned positions, so callers must use the wrapper for arbitrary seeks. Executor lifecycle is external.

## Test Signals
`TestECBlockReconstructedStripeInputStream` is extensive and covers missing indexes, parity selection, padding, full and partial stripes, offline recovery, failed datanodes, retries, insufficient locations, seek alignment, resource cleanup, and decoder integration. `TestECBlockReconstructedInputStream` covers wrapper-level behavior.
