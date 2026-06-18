# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/KeyMetadataAware.java

Purpose: This interface identifies streams that expose mutable key metadata associated with an Ozone key write.

Important APIs and types: It declares only `Map<String, String> getMetadata()`.

Control flow: Output wrappers and cipher wrappers use this interface to retrieve the metadata map from the underlying key stream even when the stream is wrapped.

State and persistence behavior: The interface has no state. Implementations usually return a live metadata map that is later merged into `OmKeyArgs` before OM commit or hsync.

Dependencies and integration points: Implemented by key output streams, wrapper streams, and `CipherOutputStreamOzone`. It supports metadata additions by higher layers without exposing concrete stream classes.

Risks: The contract does not specify mutability, nullability, or thread safety. Some wrappers cast blindly to this interface, so incompatible stream composition fails at runtime.

Test signals: Tests should verify metadata map identity through wrapper layers, mutation before close reaches OM commit arguments, and clear failure behavior for non-aware wrapped streams.
