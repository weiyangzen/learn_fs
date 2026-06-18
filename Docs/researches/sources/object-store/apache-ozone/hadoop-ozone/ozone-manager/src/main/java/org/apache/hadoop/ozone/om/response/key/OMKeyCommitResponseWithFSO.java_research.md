# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyCommitResponseWithFSO.java

Purpose: `OMKeyCommitResponseWithFSO` commits an open FSO file into the file table using object-ID path keying.

Important APIs and types: It extends `OMKeyCommitResponse`, stores volume ID, calls `OMFileRequest.addToFileTable`, and returns `BucketLayout.FILE_SYSTEM_OPTIMIZED`.

Control flow: The override deletes or updates the open-file entry depending on hsync, writes the committed file table entry, updates deleted table and any open key to update, then writes bucket used-bytes state.

State and persistence behavior: It mutates open-file, file, deleted, and bucket tables rather than legacy open-key/key tables.

Dependencies and integration points: It integrates FSO commit request logic, file-table helpers, hsync semantics, and quota accounting.

Risks and test signals: Tests should assert object-ID file-table keying, hsync open-file behavior, deleted-table updates, bucket layout override, and failure constructor no-op.
