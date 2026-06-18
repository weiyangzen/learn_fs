# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyDeleteResponseWithFSO.java

Purpose: `OMKeyDeleteResponseWithFSO` persists deleting a single FSO file or directory.

Important APIs and types: It extends `OMKeyDeleteResponse`, stores full key name, directory/file flag, volume ID, and uses directory, file, deleted-dir, deleted, open-file, and bucket tables.

Control flow: It builds the object-ID DB key. Directory deletes remove from directory table and add to deleted-dir table. File deletes set full key name on `OmKeyInfo`, delete from file table, and add to deleted table. It updates bucket state and optional hsync open-file metadata.

State and persistence behavior: Directory deletions are moved to deleted-dir table for recursive purge; file deletions move block metadata to deleted table. Bucket accounting and open-file cleanup metadata may change.

Dependencies and integration points: It integrates FSO delete request logic, directory purge service, open-key cleanup service, and bucket quota accounting.

Risks and test signals: Tests should cover file versus directory branches, full key-name mutation, deleted-dir key format, hsync cleanup, and layout override.
