<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/sst_file_writerjni.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/sst_file_writerjni.cc

Purpose: Bridges Java `SstFileWriter` to C++ `ROCKSDB_NAMESPACE::SstFileWriter` for generating external SST files.

Important APIs/types/functions: Constructors create writers with `EnvOptions`, `Options`, and optionally a comparator handle/type. `open` starts an SST file. `put`, `merge`, and `delete` are exposed for slice handles, byte arrays, and direct buffers. `fileSize` returns current file size, `finish` completes the file, and `disposeInternalJni` deletes the writer.

Control flow: Java constructs the writer, opens a path, appends sorted operations, finishes, and later ingests the file through DB APIs. Byte-array variants pin key/value arrays, create `Slice`s, call the writer API, release arrays, and throw on non-OK status. Direct put uses `JniUtil::kv_op_direct`.

State and persistence behavior: The writer creates and mutates an SST file on disk. Native state tracks open writer state until finish/dispose.

Dependencies and integration points: Includes generated `org_rocksdb_SstFileWriter.h`, RocksDB comparator/env/options/SST writer headers, conversion utilities, and `portal.h`. It integrates with comparator JNI callbacks and external file ingestion in `rocksjni.cc`.

Risks: Comparator type values are magic bytes with no default error path; an unknown type silently uses a null comparator. The byte-array method comments contain mismatched signatures but implementation is clear. Java must enforce key ordering and finish semantics; RocksDB returns errors otherwise. Direct-buffer offset correctness is delegated to `JniUtil`.

Test signals: Tests should write a valid SST with byte-array and slice APIs, use a custom comparator path, verify file size and checksum through `SstFileReader`, test merge/delete entries, test direct-buffer offsets, and assert errors for unsorted keys or double finish.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/sst_file_writerjni.cc -->
