# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/WriteOptionsTest.java

Purpose: JUnit coverage for RocksJava `WriteOptions` option setters/getters and native copy-constructor behavior.

Important APIs/types/functions: `WriteOptions.setSync`, `sync`, `setDisableWAL`, `disableWAL`, `setIgnoreMissingColumnFamilies`, `setNoSlowdown`, `setLowPri`, `setMemtableInsertHintPerBatch`, and `new WriteOptions(origOpts)`.

Control flow and state: `writeOptions()` creates one native-backed options object and toggles each boolean true then false, asserting the Java getter mirrors the native value. `copyConstructor()` randomizes several booleans on the original, sets `memtableInsertHintPerBatch`, copies, and compares values.

State and persistence behavior: this is transient JNI option state only; no database is opened and no persisted write behavior is tested.

Dependencies and integration points: depends on RocksJava native library loading and `PlatformRandomHelper` for platform-specific randomness. These options feed DB write paths elsewhere.

Risks: coverage is limited to boolean round-trips; it does not prove `noSlowdown`, `lowPri`, WAL disabling, or sync change write behavior under load. `copyConstructor()` omits some toggled properties such as `noSlowdown` and `lowPri`.

Test signals: basic native handle construction, mutability, and copy propagation are covered.
