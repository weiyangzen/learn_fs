# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyCreateResponseWithFSO.java

Purpose: `OMKeyCreateResponseWithFSO` is the FSO key-create response and delegates to the FSO file-create implementation.

Important APIs and types: It extends `OMFileCreateResponseWithFSO`, accepts `OmKeyInfo`, parent `OmDirectoryInfo` list, open key session ID, bucket info, and volume ID, and cleans directory, open-file, and bucket tables.

Control flow: All DB behavior is inherited: write parent directories, update bucket namespace state, and add the open file entry.

State and persistence behavior: It writes open-file table state and directory-table parent entries, not committed file table state.

Dependencies and integration points: It bridges key create request variants to file-system-optimized persistence helpers.

Risks and test signals: Tests should confirm inherited FSO behavior, constructor parameter propagation, cleanup annotation, and error response handling.
