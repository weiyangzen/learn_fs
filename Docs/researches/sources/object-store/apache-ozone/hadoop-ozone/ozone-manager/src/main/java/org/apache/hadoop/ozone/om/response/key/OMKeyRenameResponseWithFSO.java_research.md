# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyRenameResponseWithFSO.java

Purpose: `OMKeyRenameResponseWithFSO` persists renaming an FSO file or directory and optional parent/bucket updates.

Important APIs and types: It extends `OMKeyRenameResponse`, tracks whether the target is a directory, optional from/to parent `OmKeyInfo`, bucket info, and uses `OMFileRequest.getDirectoryInfo`.

Control flow: It gets volume and bucket IDs, deletes the old directory or file row, writes the new directory or file row, writes snapshot-renamed metadata if needed, writes updated parent directory rows for source/target parents, and writes bucket table when provided.

State and persistence behavior: It mutates directory table or file table, snapshot renamed table, optional parent directory rows, and optional bucket quota state.

Dependencies and integration points: It integrates FSO rename request validation, object-ID keying, snapshot tracking, and quota updates.

Risks and test signals: Tests should cover file and directory rename branches, parent directory updates, snapshot marker behavior, bucket updates, and layout override.
