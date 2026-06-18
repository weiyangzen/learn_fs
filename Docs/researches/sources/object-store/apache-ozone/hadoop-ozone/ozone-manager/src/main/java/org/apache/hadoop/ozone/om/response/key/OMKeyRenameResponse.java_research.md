# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyRenameResponse.java

Purpose: `OMKeyRenameResponse` persists renaming one key in non-FSO/default key tables and records snapshot rename metadata when needed.

Important APIs and types: It stores from/to key names and updated `OmKeyInfo`, cleans `KEY_TABLE` and `SNAPSHOT_RENAMED_TABLE`, and uses `OMClientRequestUtils.isSnapshotBucket`.

Control flow: `addToDBBatch` deletes the old key-table row, writes the new key-table row, then if the bucket is in snapshot scope and no rename marker exists, writes snapshot-renamed table entry keyed by object ID.

State and persistence behavior: It atomically moves the key-table entry and may persist snapshot rename provenance.

Dependencies and integration points: It integrates key rename requests, snapshot diff/cleanup tracking, and metadata-manager key helpers.

Risks and test signals: Tests should cover normal rename, snapshot bucket rename marker creation, existing marker preservation, and failed response no-op.
