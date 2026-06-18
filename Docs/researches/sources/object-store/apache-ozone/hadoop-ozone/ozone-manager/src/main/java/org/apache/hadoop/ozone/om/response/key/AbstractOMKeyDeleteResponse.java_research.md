# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/AbstractOMKeyDeleteResponse.java

Purpose: `AbstractOMKeyDeleteResponse` centralizes the DB-batch operation for deleting a key from one table and moving its block metadata to the deleted table.

Important APIs and types: It extends `OmKeyResponse` and provides two overloads of `addDeletionToBatch`, one for normal key names and one for FSO full delete-key names. It uses `OmKeyInfo.isKeyEmpty`, `OmUtils.prepareKeyForDelete`, `RepeatedOmKeyInfo`, and `Table<String, ?>`.

Control flow: The helper deletes the source table entry, skips empty keys, marks `OmKeyInfo` with committed-key-deleted flag, wraps it in `RepeatedOmKeyInfo`, builds the deleted-table key, and writes the deleted table.

State and persistence behavior: It performs batch mutations only; it does not commit. It deletes from key/open/file source tables and adds non-empty keys to the common deleted table for async block cleanup.

Dependencies and integration points: All single-key, multi-key, open-key, and FSO delete responses use this helper.

Risks and test signals: Tests should cover empty-key skip behavior, committed versus open-key deletion flag, FSO full-key deleted-table naming, duplicate object IDs, and source table deletion.
