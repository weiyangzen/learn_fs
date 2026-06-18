# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeySetTimesResponseWithFSO.java

Purpose: `OMKeySetTimesResponseWithFSO` persists timestamp changes for FSO files or directories.

Important APIs and types: It extends `OMKeySetTimesResponse`, stores `isDirectory`, volume ID, bucket ID, and converts key info to `OmDirectoryInfo` for directory rows.

Control flow: It builds the FSO object-ID path key. Directory targets are written to directory table; file targets are written to the file/key table for the FSO bucket layout.

State and persistence behavior: It updates either `DIRECTORY_TABLE` or `FILE_TABLE` metadata and does not update quota counters.

Dependencies and integration points: It integrates FSO set-times request logic, `OMFileRequest.getDirectoryInfo`, and layout-specific table routing.

Risks and test signals: Tests should cover both directory and file branches, path-key generation, timestamp persistence, and error response no-op.
