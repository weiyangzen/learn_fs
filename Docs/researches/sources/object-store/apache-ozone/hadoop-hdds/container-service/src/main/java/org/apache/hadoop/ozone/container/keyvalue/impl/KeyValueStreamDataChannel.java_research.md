## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/KeyValueStreamDataChannel.java

Purpose: Implements the Ratis `StateMachine.DataChannel` used by key-value containers for streaming writes, buffering incoming `ByteBuffer` data and writing only the chunk payload to the block file.

Important APIs and functions: `write()` records StreamWrite metrics, checks closed state and container space, and delegates to `writeBuffers()`. `writeBuffers(ReferenceCountedObject, Buffers, WriteMethod)` drains whole buffers and releases references. `writeFully()` loops until the file channel accepts all bytes. `close()` flushes buffered content before closing. `setEndIndex()` and `readProtoLength()` strip the trailing PutBlock proto from the stream frame.

Control flow and state: The instance owns a `Buffers` accumulator and an atomic `closed` flag. Normal writes feed the accumulator; close polls all remaining bytes, moves the Netty writer index to the start of the trailing proto, writes payload bytes, releases the retained buffer, then closes the base channel. `cleanupInternal()` drops all buffered data and closes if the stream was never linked.

Persistence and dependencies: File persistence is inherited from `StreamDataChannelBase` over `RandomAccessFile`/`FileChannel`. It integrates with Ratis reference-counted buffers, Netty `ByteBuf`, `RatisHelper` debug logging, `ContainerMetrics`, and `ContainerData` space accounting.

Risks: Reference counting must remain balanced across offered buffers and the final `pollAll()` retain/release pair. `setEndIndex()` assumes the last four bytes encode proto length; corrupt or partial frames can set an invalid writer index. Returning `src.get().remaining()` after offers means callers depend on buffer mutation semantics. A non-positive file-channel write is treated as fatal.

Test signals: Cover stream writes split across frame boundaries, close with trailing PutBlock proto, malformed proto lengths, writes after close, cleanup of unlinked channels, reference release under exceptions, and metrics/space accounting for payload bytes only.
