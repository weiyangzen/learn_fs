# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeysDeleteResponse.java

Purpose: `OMKeysDeleteResponse` persists multi-key deletion in default layouts and supports partial-delete status.

Important APIs and types: It extends `AbstractOMKeyDeleteResponse`, stores a list of `OmKeyInfo`, bucket info, and open-key metadata map. It overrides `checkAndUpdateDB` to accept `OK` and `PARTIAL_DELETE`.

Control flow: For each key it derives the ozone key and calls `addDeletionToBatch` against the key table. It updates bucket state and writes any open-key info entries used by cleanup service.

State and persistence behavior: It deletes multiple key-table rows, writes deleted-table entries for non-empty keys, updates bucket table, and may write open-key table metadata.

Dependencies and integration points: It integrates bulk key delete request logic, partial success response status, bucket quota accounting, and hsync/open-key cleanup.

Risks and test signals: Tests should cover partial delete persistence, multiple deleted-table entries, bucket update, open-key info map, and failed statuses that must not write.
