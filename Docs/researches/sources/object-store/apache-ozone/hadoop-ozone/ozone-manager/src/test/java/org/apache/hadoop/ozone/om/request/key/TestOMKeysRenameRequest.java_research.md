## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeysRenameRequest.java

**Purpose:** Tests batch key rename in object-store layout for all-success and partial-rename cases.

**Important APIs/types/functions:** Uses `OMKeysRenameRequest`, `RenameKeysRequest`, `RenameKeysArgs`, `RenameKeysMap`, `OMClientResponse`, `OmKeyInfo`, and `OMRequestTestUtils.addKeyToTableCache`.

**Control flow:** `createRenameKeyRequest` seeds volume/bucket and ten source keys under `/test`, builds a list of source-to-destination mappings (`keyN` to `newKeyN`), and optionally appends an illegal/nonexistent mapping. Tests validate/update cache and inspect response success/status and table rows.

**State and persistence behavior:** Successful mappings remove source key-table rows and create destination rows. Partial failure still applies valid renames and reports the failed mapping in `RenameKeysResponse.unRenamedKeys`.

**Dependencies and integration points:** Integrates batch rename with per-key response aggregation and key-table cache mutation. Unlike single rename tests, this class focuses on batch semantics and partial success reporting.

**Risks:** Risks include stopping at the first failed mapping, leaving valid source keys after partial failure, not creating destination rows, missing failed mapping details, and response success boolean not matching `PARTIAL_RENAME`.

**Test signals:** Assertions check `OK` or `PARTIAL_RENAME`, response success booleans, source null/destination non-null for all valid mappings, and `unRenamedKeys[0].fromKeyName == "testKey"` for the injected failure.
