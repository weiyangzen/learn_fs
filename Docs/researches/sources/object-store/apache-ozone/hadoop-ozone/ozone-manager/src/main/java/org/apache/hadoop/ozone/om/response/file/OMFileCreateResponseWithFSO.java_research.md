# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/file/OMFileCreateResponseWithFSO.java

Purpose: `OMFileCreateResponseWithFSO` persists file creation for FSO buckets, including parent directories and open-file table state.

Important APIs and types: It extends `OMFileCreateResponse`, stores parent `OmDirectoryInfo` list and volume ID, uses `OMFileRequest.addToOpenFileTable`, and returns `BucketLayout.FILE_SYSTEM_OPTIMIZED`.

Control flow: It writes parent directories when present, updates bucket table for namespace changes, then adds the file to the open-file table using volume and bucket object IDs.

State and persistence behavior: It writes directory-table parent rows, bucket-table quota state, and open-file table entries. It does not write a committed file table row until commit.

Dependencies and integration points: It integrates file-create request data, FSO object-ID keying, and `OMFileRequest` helper methods.

Risks and test signals: Tests should verify parent directory persistence, open-file key format, bucket update, layout override, and no stale parent creation assumptions noted by the TODO.
