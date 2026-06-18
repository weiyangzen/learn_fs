## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeysDeleteRequest.java

**Purpose:** Tests batch key delete for object-store layout, including all-success and partial-delete outcomes.

**Important APIs/types/functions:** Uses `OMKeysDeleteRequest`, `DeleteKeysRequest`, `DeleteKeyArgs`, `DeleteKeyError`, `OMClientResponse`, and `OMRequestTestUtils.addKeyToTableCache`. Helper methods `createPreRequisites`, `checkDeleteKeysResponse`, and `checkDeleteKeysResponseForFailure` are reused by the FSO subclass.

**Control flow:** Setup creates volume/bucket metadata and ten keys under `/user`, adds each key to the delete request, and stores the request/list on the test instance. Success validation expects `OMResponse.success=true`, `Status.OK`, no undeleted keys, no errors, and all key-table rows removed. Failure appends a nonexistent `dummy` key and expects partial status while existing keys are still deleted.

**State and persistence behavior:** The test works against the key table cache. Existing keys are removed from `keyTable`; nonexistent keys are reported in `DeleteKeysResponse.unDeletedKeys` and `errorsList` without preventing deletion of valid keys.

**Dependencies and integration points:** Integrates batch delete request code with response aggregation and per-key error reporting. It depends on seeded cache entries rather than committed DB rows, which exercises cache-aware delete lookup.

**Risks:** Risks include all-or-nothing behavior when partial deletion is expected, missing per-key errors, undeleted key list not matching failed inputs, and cache/table mismatch after batch mutation.

**Test signals:** OK vs `PARTIAL_DELETE` status, response boolean fields, unDeleted key count/name, error count, and null key-table lookups for every valid key provide coverage.
