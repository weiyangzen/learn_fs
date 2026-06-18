# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyRenameResponse.java

Purpose: Tests single-key rename response behavior for legacy and, through subclass hooks, FSO layout.

Important APIs/types/functions: Uses `OMKeyRenameResponse`, `OmKeyInfo`, `snapshotRenamedTable`, `getRenameKey`, key table methods, and subclass extension points for FSO parent/bucket handling.

Control flow: The success test creates source and target key infos, adds the source to the key table, constructs a rename response, asserts source exists and target absent, commits response, then asserts the source row is gone and target row exists. It also verifies snapshot rename table is not populated for a non-snapshot bucket. The error test uses KEY_NOT_FOUND and verifies no DB changes.

State/persistence: Success moves a key-table row from old DB key to new DB key. FSO branches additionally expect parent directory rows and bucket row to be persisted by the FSO response.

Dependencies/integration: Provides overridable helpers for DB key computation and response construction used by the FSO subclass.

Risks/test signals: Snapshot-bucket rename behavior is not exercised, only the negative case. Error-path assertions focus on key table and FSO parent rows.
