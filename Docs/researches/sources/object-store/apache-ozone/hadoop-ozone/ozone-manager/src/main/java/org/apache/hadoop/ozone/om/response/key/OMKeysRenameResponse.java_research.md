# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeysRenameResponse.java

Purpose: `OMKeysRenameResponse` persists batch key renames in default layouts and supports partial rename.

Important APIs and types: It extends `OMClientResponse`, stores `OmRenameKeys`, cleans `KEY_TABLE` and `SNAPSHOT_RENAMED_TABLE`, and accepts `OK` or `PARTIAL_RENAME` in `checkAndUpdateDB`.

Control flow: For each from-to mapping it deletes the old key-table row, writes the new key-table row, and records a snapshot-renamed entry when the bucket is snapshot-scoped and no marker exists.

State and persistence behavior: It performs multiple key-table moves and optional snapshot-renamed table writes in one batch.

Dependencies and integration points: It integrates bulk rename request logic, snapshot tracking, and metadata key helpers.

Risks and test signals: Tests should cover partial rename persistence, multiple mapping order, snapshot marker idempotence, failed response no-op, and object ID keying for rename markers.
