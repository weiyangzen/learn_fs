## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyDeleteRequest.java

**Purpose:** Tests single-key delete behavior in object-store layout, including preExecute user-info mutation, reserved snapshot path rejection, success deletion, and missing key/volume/bucket errors.

**Important APIs/types/functions:** Uses `OMKeyDeleteRequest`, `DeleteKeyRequest`, `KeyArgs`, `OMClientResponse`, `OmKeyInfo`, and `OMRequestTestUtils`. Helpers include `doPreExecute`, `createDeleteKeyRequest`, `addKeyToTable`, and `getOmKeyDeleteRequest`.

**Control flow:** Parameterized preExecute tests seed a key, build delete requests for plain and snapshot-containing non-reserved paths, and assert preExecute returns a changed request. Failure cases call preExecute with `.snapshot` root/reserved paths and assert `OMException.INVALID_KEY_NAME`. Validate/update tests seed or omit volume/bucket/key state and check status codes.

**State and persistence behavior:** A successful delete removes the key from `keyTable` in cache. Error cases leave the table unchanged or empty. The object-store DB key is computed with `getOzoneKey(volume,bucket,key)`.

**Dependencies and integration points:** Relies on shared metadata setup, `OMRequestTestUtils.addKeyToTable`, and `BucketLayout.DEFAULT`. It integrates with snapshot-reserved name validation and OM response status mapping.

**Risks:** Risks include allowing deletes under the reserved snapshot namespace, deleting from the wrong bucket layout table, treating missing volume/bucket as key-not-found, and leaving visible key-table entries after successful cache update.

**Test signals:** Assertions check exception messages/result codes, OK/KEY_NOT_FOUND/VOLUME_NOT_FOUND/BUCKET_NOT_FOUND statuses, and null/non-null key-table lookups before and after delete.
