## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyRenameRequest.java

**Purpose:** Tests single-key rename in object-store layout, covering preExecute modification time/user-info changes, successful key-table move, and key/volume/bucket/invalid-name error paths.

**Important APIs/types/functions:** Uses `OMKeyRenameRequest`, `RenameKeyRequest`, `KeyArgs`, `OmKeyInfo`, `OMClientResponse`, and `OMRequestTestUtils`. Helpers include `createParentKey`, `createRenameKeyRequest`, `doPreExecute`, `getOmKeyInfo`, `addKeyToTable`, `getDBKeyName`, and `assertModificationTime`.

**Control flow:** `@BeforeEach` seeds volume/bucket and initializes from/to names and destination DB key. Success tests add a source key, pre-execute rename, validate/update cache, and assert the old key is gone while the destination exists. Error tests omit source/volume/bucket or pass empty names and assert status codes.

**State and persistence behavior:** Successful rename deletes the source `keyTable` row and writes an updated `OmKeyInfo` at the destination ozone key. The destination key's modification time must match the pre-executed request's `KeyArgs.modificationTime`.

**Dependencies and integration points:** Integrates rename request logic with key table cache mutation and bucket layout selection. It depends on `Path` normalization for simple source/destination names and shared OM metadata fixtures.

**Risks:** Risks include losing key metadata during row move, not updating modification time, allowing invalid names, misclassifying missing volume/bucket/source errors, or leaving duplicate source/destination rows.

**Test signals:** OK/error statuses, null source lookup, non-null destination lookup, and exact modification time equality indicate correct behavior.
