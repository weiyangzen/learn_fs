# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeySetTimesRequestWithFSO.java

Purpose: `OMKeySetTimesRequestWithFSO` updates modification time for files or directories in FSO buckets. It reuses the base preExecute ACL handling but writes to the FSO file table or directory table according to the resolved path type.

Important APIs and types: The class extends `OMKeySetTimesRequest` and uses `OzoneFileStatus`, `OMFileRequest.getOMKeyInfoIfExists`, `OmDirectoryInfo`, `OmKeyInfo`, `OMKeySetTimesResponseWithFSO`, FSO path keys, `OzoneFSUtils`, and table cache entries.

Control flow: `preExecute` delegates to the parent. `validateAndUpdateCache` acquires the bucket lock, resolves the requested path to `OzoneFileStatus`, fails on missing key, rewrites the key info name to the leaf file name, computes the FSO DB key from volume ID, bucket ID, parent object ID, and file name, applies the mtime through the parent hook, sets update ID, writes either a directory-table cache entry or key-table cache entry, returns an FSO set-times response with directory flag and IDs, releases the lock, and invokes the shared audit completion hook.

State and persistence behavior: Directory mtimes persist through `OmDirectoryInfo` cache values; file mtimes persist through key-table `OmKeyInfo` cache values. Bucket quota and namespace do not change. The response carries the layout, volume ID, bucket ID, and is-directory flag so batch persistence can choose the correct table.

Dependencies and integration points: It depends on FSO path lookup, directory-info conversion in `OMFileRequest`, bucket locks, base ACL/audit logic, and FSO response persistence. It uses the OM default replication config only to build file status for lookup.

Risks: Unlike the base class, this method does not explicitly reject mtime less than `-1`; it relies on shared `apply` behavior and therefore may accept invalid values without changing mtime if the validation is not performed elsewhere. The leaf-name rewrite is required for FSO table format and must not leak full path into the DB row. Directory versus file response handling must stay synchronized with response batch code.

Test signals: `TestOMSetTimesRequestWithFSO` should verify file and directory updates, correct table choice, missing-key failure, leaf-name storage, response volume/bucket IDs, audit completion, `-1` behavior, and parity or intentional divergence for invalid negative mtimes compared with the base request.
