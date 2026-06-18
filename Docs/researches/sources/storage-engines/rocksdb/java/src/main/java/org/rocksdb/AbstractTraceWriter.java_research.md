# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractTraceWriter.java

- **Purpose:** Base callback bridge for Java trace writers used by RocksDB tracing.
- **Important APIs/types/functions:** Extends `RocksCallbackObject` and implements `TraceWriter`. `initializeNative()` calls `createNewTraceWriter()`. Private JNI callback proxies `writeProxy(long sliceHandle)` and `closeWriterProxy()` translate Java `RocksDBException` into packed status shorts. `statusToShort` packs `Status.Code` and `Status.SubCode`.
- **Control flow:** Native code calls the private proxy methods. `writeProxy` wraps the borrowed native slice handle in a non-owning `Slice`, calls user `write(Slice)`, and returns OK or the exception status. `closeWriterProxy` calls `closeWriter()` and performs the same status conversion. Null status/code values fall back to `IOError`/`None`.
- **State and persistence behavior:** Trace persistence is delegated to subclass `write`/`closeWriter` implementations; this class only manages native callback bridging and status encoding.
- **Dependencies:** Depends on `RocksCallbackObject`, `TraceWriter`, `Slice`, `Status`, and `RocksDBException`; native code must decode the short in the same high-byte/low-byte layout.
- **Integration points:** Used by RocksDB tracing APIs to let Java write trace records to custom sinks while native code receives RocksDB-style status results.
- **Risks:** The slice handle is borrowed; Java code must not retain it beyond callback lifetime. Status packing is only two bytes and must stay aligned with enum values. Unexpected unchecked exceptions are not caught and can cross JNI poorly.
- **Test signals:** Successful write/close callbacks, exception-to-status-code translation, null-status fallback, short packing compatibility, and borrowed slice lifetime behavior.
