# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/file/OMDirectoryCreateResponseWithFSO.java

Purpose: `OMDirectoryCreateResponseWithFSO` persists directory creation for file-system-optimized buckets using directory table object-ID path keys.

Important APIs and types: It stores `OmDirectoryInfo`, parent directory infos, volume ID, bucket ID, result, bucket info, and cleans `DIRECTORY_TABLE`.

Control flow: `addToDBBatch` delegates to `addToDirectoryTable`. If `dirInfo` is present, it writes parent directories, writes the target directory, and updates bucket table. If absent, it logs an OK no-op for existing directories.

State and persistence behavior: It writes directory-table rows keyed by `(volumeId,bucketId,parentObjectId,name)` and updates bucket-table namespace state.

Dependencies and integration points: It integrates FSO directory request logic, metadata-manager path-key generation, and bucket quota accounting.

Risks and test signals: Tests should assert object-ID keying, parent directory creation, existing-directory no-op, bucket update, and cleanup table annotation completeness.
