<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneFSDataStreamOutput.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneFSDataStreamOutput.java

## Purpose
ByteBuffer-oriented output stream wrapper for Ozone datastream writes.

## Important APIs, types, and functions
Extends `ByteBufferOutputStream`, wraps `ByteBufferStreamOutput`, and implements `write(ByteBuffer,int,int)`, `flush`, `close`, `hflush`, `hsync`, and a protected accessor for capability wrappers.

## Control flow
Every operation delegates directly to the underlying datastream output. `hflush` aliases to `hsync`; `hsync` runs inside a tracing span.

## State and persistence behavior
Local state is the wrapped datastream. Data durability and block/container persistence are handled by Ozone datastream internals.

## Dependencies and integration points
Created by adapter `createStreamFile` and selected by `BasicRootedOzoneFileSystem` or `BasicOzoneFileSystem` when datastream is enabled and the selector threshold is exceeded. Hadoop 3 capability wrappers reuse the protected accessor.

## Risks and test signals
The wrapper is thin, so risks are mostly capability and lifecycle mismatches: close/flush must propagate exactly once, hsync must map to datastream sync semantics, and byte-buffer slices must be honored. Tests should write heap and direct buffers through datastream mode and verify persisted content and sync behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneFSDataStreamOutput.java -->
