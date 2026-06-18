## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/checksum/AbstractBlockChecksumComputer.java

### Purpose
`AbstractBlockChecksumComputer` defines the minimal contract for computing a block-level checksum from chunk checksums under a selected checksum combine mode.

### Important APIs and Types
Subclasses implement `compute(OzoneClientConfig.ChecksumCombineMode)`. The base stores an output `ByteBuffer`, exposed by `getOutByteBuffer`, and provides `setOutBytes` to wrap result bytes.

### Control Flow
The base class has no checksum algorithm; callers invoke `compute`, then read the output buffer.

### State and Persistence Behavior
The only state is the computed output buffer. It is local and overwritten when subclasses call `setOutBytes`.

### Dependencies and Integration Points
It is used by `BaseFileChecksumHelper` and implemented by `ReplicatedBlockChecksumComputer` and `ECBlockChecksumComputer`.

### Risks and Edge Cases
The API does not enforce that `compute` was called before `getOutByteBuffer`. `setOutBytes` wraps the provided array without copying, so later array mutation could alter the buffer content if callers kept a reference.

### Test Signals
Tests should focus on subclass behavior and verify output buffer is set for each combine mode and rejected for unsupported modes.
