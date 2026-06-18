# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/FileOperationInfo.java

Purpose: Java representation of `FileOperationInfo` from RocksDB listener APIs. It captures path, offset, length, start timestamp, duration, and `Status` for file operations.

Control flow is package-private construction from JNI, getters, and value-object equality/hash/toString. State is copied Java data used by `EventListener` callbacks such as file read/write/flush/sync events. There is no Java persistence, but timestamp/duration units are nanoseconds according to comments. Dependencies include `Status`, `Objects`, and listener native payload conversion.

Risks: status object semantics and nullability depend on native conversion; timestamp origin must match C++ docs; large offsets/lengths require long precision. Tests should validate callback payloads, equality/hash, failed-operation statuses, and unit expectations for duration fields.
