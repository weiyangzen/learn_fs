# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Experimental.java

Purpose: source-retention annotation marking APIs that may change, be removed, or be re-engineered.

Control flow is declarative Java annotation metadata: `@Documented`, `@Retention(SOURCE)`, and `@Target(TYPE, METHOD)`, with one required `String value()`. It has no runtime state, native dependency, or persistence behavior. Integration points include experimental classes and methods such as `HyperClockCache` and selected compaction stats.

Risks: because retention is SOURCE, runtime reflection cannot detect it; tooling must inspect sources or generated docs. Tests are mostly compile/documentation checks verifying intended APIs are annotated and no runtime dependency assumes retention.
