# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/EncodingType.java

Purpose: enum for block/table encoding choices, including plain, prefix, and reserved values.

Control flow is immutable byte mapping through `getValue()` with no reverse lookup in this file. State is consumed by table configuration JNI and native RocksDB encoding logic; Java does not persist it directly. Dependencies are table option classes that accept encoding values.

Risks: reserved/native values must remain aligned, and unsupported encodings could be accepted until native validation. Tests should verify bytes through option round-trips and table creation/readback with supported encodings.
