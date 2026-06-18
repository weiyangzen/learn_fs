# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ExternalFileIngestionInfo.java

Purpose: immutable Java value object for external SST ingestion event data. It records column family name, external file path, internal DB file path, assigned global sequence number, and `TableProperties`.

Control flow is package-private construction from JNI/tests, public getters, and value-object `equals`, `hashCode`, and `toString`. State is copied into Java fields, so it can safely outlive the callback if nested `TableProperties` is also safe. Dependencies include `Objects`, `TableProperties`, and `EventListener` ingestion callbacks.

Risks: equality depends on `TableProperties.equals`, paths are raw strings, and constructor visibility means production instances originate from native code. Tests should compare value semantics, callback payload population, null field handling if native permits it, and sequence-number correctness for ingested files.
