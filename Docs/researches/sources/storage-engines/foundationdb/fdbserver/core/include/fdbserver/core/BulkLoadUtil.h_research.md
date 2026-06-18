# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/BulkLoadUtil.h

## sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/BulkLoadUtil.h

Purpose: declares file and metadata utilities used by bulk load to stage, copy, sample, download, and interpret dumped file sets.

Important APIs: `clearFileFolder`, `resetFileFolder`, `copyBulkFile`, `readBulkFileBytes`, `writeBulkFileBytes`, `getBulkLoadTaskStateFromDataMove`, `bulkLoadDownloadTaskFileSet`, `bulkLoadDownloadTaskFileSets`, `doBytesSamplingOnDataFile`, `downloadBulkLoadJobManifestFile`, `getBulkLoadJobFileManifestEntryFromJobManifestFile`, and `getBulkLoadManifestMetadataFromEntry`.

Control flow and state: folder helpers erase or recreate local staging directories. Async file helpers copy/read/write with maximum byte limits. Data-move metadata lookup waits for the relevant `BulkLoadTaskState` at or after a version. Download helpers move remote file sets into local roots. Sampling produces byte-sample files from data files. Manifest helpers download a job manifest, extract entries intersecting a key range, and fetch manifest metadata for those entries.

State and persistence behavior: operates on local files, remote bulk-load storage, and data-move metadata persisted in FDB. Some actors can remain pending if required metadata reads fail, per comment.

Dependencies and integration: depends on `fdbclient/BulkLoading.h`, database transactions, transports, manifests, file sets, and data movement IDs. It bridges DD bulk-load metadata and storage-server local ingest preparation.

Risks and tests: file byte limits protect memory and disk. Folder clearing must avoid deleting wrong paths. Manifest range extraction must avoid gaps/overlaps. Tests should cover transport errors, oversized files, missing manifest entries, sampling correctness, and data-move version waits.
