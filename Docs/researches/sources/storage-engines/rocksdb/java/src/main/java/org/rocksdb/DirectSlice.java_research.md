# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/DirectSlice.java

Purpose: direct-`ByteBuffer` backed slice implementation for efficient native data access, especially for larger keys/values. It extends `AbstractSlice<ByteBuffer>` and exposes `NONE`.

Control flow has three construction paths: package-private JNI/default without native object, string constructor that allocates internal native buffer, and direct `ByteBuffer` constructors that require `data.isDirect()`. Accessors call native methods for `data0`, `get`, `clear`, `removePrefix`, and `setLength`. `removePrefix` advances `internalBufferOffset`; `disposeInternal` frees internal string buffer only if it has not been cleared, then disposes the slice handle.

State includes native slice handle, whether Java owns internal buffer memory, cleared flag, and offset. Dependencies include `AbstractSlice`, direct `ByteBuffer`, and native slice helpers.

Risks: non-direct buffers throw, internal buffer ownership/offset must be exact to avoid leaks or double free, volatile flags protect visibility but not full lifecycle synchronization, and disposed slices invalidate native access. Tests should cover string and direct-buffer construction, prefix removal before clear/dispose, setLength/get bounds through native code, and `NONE` behavior.
