# sources/storage-engines/rocksdb/table/sst_file_writer_collectors.h

Purpose: defines table-property collector support for marking SST files created by `SstFileWriter`.

Important APIs/types/functions: `ExternalSstFilePropertyNames` declares `kVersion` and `kGlobalSeqno`. `SstFileWriterPropertiesCollector` implements `InternalTblPropColl`, ignores per-key/block stats, and writes fixed-width version/global-seqno properties in `Finish`. `SstFileWriterPropertiesCollectorFactory` creates collectors with configured version and global sequence number.

Control flow: during table building, the factory creates a collector; each key/block callback is a no-op; `Finish` serializes version with `PutFixed32` and global seqno with `PutFixed64` into user collected properties.

State and persistence behavior: collector state is only `version_` and `global_seqno_`; persisted state is two user-collected table properties embedded in the SST. Readable properties expose the version as text.

Dependencies/integration points: used by `SstFileWriter::Open` as part of `InternalTblPropCollFactories`. Reader/test code detects these properties through `ExternalSstFilePropertyNames`.

Risks: readable properties omit global sequence number, so diagnostics needing it must inspect raw user properties. The collector does not validate or update values after construction.

Test signals: `ReadFileWithGlobalSeqno` checks that external SST properties include `kGlobalSeqno` after ingestion, and writer-created files are recognized through `CreatedBySstFileWriter`.
