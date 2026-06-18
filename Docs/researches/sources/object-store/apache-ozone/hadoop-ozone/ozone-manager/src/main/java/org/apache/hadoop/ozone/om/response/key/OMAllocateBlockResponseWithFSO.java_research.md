# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMAllocateBlockResponseWithFSO.java

Purpose: `OMAllocateBlockResponseWithFSO` persists allocated block metadata for an open FSO file.

Important APIs and types: It extends `OMAllocateBlockResponse`, stores volume and bucket IDs, and calls `OMFileRequest.addToOpenFileTable`.

Control flow: The FSO override bypasses string open-key naming and writes the open-file entry with object IDs and client ID.

State and persistence behavior: It updates `OPEN_FILE_TABLE` with the latest `OmKeyInfo` for the in-progress file.

Dependencies and integration points: It integrates FSO key allocation request logic, object-ID keying, and bucket layout routing.

Risks and test signals: Tests should verify open-file key format, volume/bucket ID use, layout-specific cleanup annotation, and inherited failure behavior.
