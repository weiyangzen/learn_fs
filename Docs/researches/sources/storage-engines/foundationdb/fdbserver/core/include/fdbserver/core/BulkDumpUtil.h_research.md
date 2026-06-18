# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/BulkDumpUtil.h

## sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/BulkDumpUtil.h

Purpose: declares utilities and data holders for bulk dump jobs, including storage-server dump task construction, local/remote file naming, manifest generation, upload, and bounded parallelism.

Important APIs/types: `RangeDumpRawData`, `SSBulkDumpTask`, `getSSBulkDumpTask`, `generateRandomBulkDumpDataFileName`, `getLocalRemoteFileSetSetting`, `persistCompleteBulkDumpRange`, `generateBulkDumpJobFolder`, `getBulkDumpJobTaskFolder`, `dumpDataFileToLocalDirectory`, `uploadBulkDumpJobManifestFile`, `uploadBulkDumpFileSet`, and `ParallelismLimitor`.

Control flow and state: `RangeDumpRawData` bundles dumped KVs, byte samples, last key, and byte count. `SSBulkDumpTask` carries target storage server, checksum server IDs, and `BulkDumpState`, with a diagnostic `toString`. File-setting helpers define deterministic local and remote manifest/data/sample paths under job/task folders. Dumping produces SST data, byte samples, and manifest metadata from a range. Upload helpers move job and task manifests/file sets through the configured transport. `ParallelismLimitor` uses an `AsyncVar<int>` counter to gate concurrent tasks and exposes `onChange`.

State and persistence behavior: bulk dump completion is persisted by writing metadata in Complete phase to bulk dump system keyspace. Local and remote files are persistent external artifacts.

Dependencies and integration: depends on bulk dumping/loading client types and storage server interfaces. Data distributor creates tasks; storage servers dump data; bulk load can later consume produced manifests.

Risks and tests: path generation must match bulk load expectations. Parallelism counters assert on over/underflow. Tests should cover empty ranges, sampled/non-sampled ranges, local/remote path symmetry, upload failure, complete-state persistence, and parallel limiter wakeups.
