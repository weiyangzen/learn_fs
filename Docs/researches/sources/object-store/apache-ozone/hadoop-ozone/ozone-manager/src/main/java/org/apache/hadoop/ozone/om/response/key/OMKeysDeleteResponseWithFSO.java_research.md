# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeysDeleteResponseWithFSO.java

Purpose: `OMKeysDeleteResponseWithFSO` persists bulk deletion of FSO files and directories.

Important APIs and types: It extends `OMKeysDeleteResponse`, stores directory delete list and volume ID, and uses directory, file, deleted-dir, deleted, open-file, and bucket tables.

Control flow: It removes each directory from directory table and writes deleted-dir table entries. It removes each file from file table and writes deleted-table entries using full delete keys. It updates bucket state and writes open-key info map entries.

State and persistence behavior: It mutates FSO directory/file namespace and queues file blocks/directories for asynchronous cleanup.

Dependencies and integration points: It integrates bulk delete requests, recursive directory purge service, FSO keying, and quota updates.

Risks and test signals: Tests should cover mixed file/directory deletes, object-ID deleted-dir keys, partial success inherited behavior, open-file metadata updates, and layout override.
