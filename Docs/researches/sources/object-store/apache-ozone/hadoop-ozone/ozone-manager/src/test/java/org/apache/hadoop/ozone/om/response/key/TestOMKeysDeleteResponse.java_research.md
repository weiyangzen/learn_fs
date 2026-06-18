# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeysDeleteResponse.java

Purpose: Tests multi-key delete response for legacy/default key layout.

Important APIs/types/functions: Uses `OMKeysDeleteResponse`, `OMClientResponse`, `DeleteKeysResponse`, `OmKeyInfo`, `RepeatedOmKeyInfo`, `RatisReplicationConfig`, and inherited key fixture tables.

Control flow: `createPreRequisities` adds ten keys under `/userkeyN`, records their `OmKeyInfo` and DB keys, and the success test constructs an OK `DeleteKeys` response, runs `checkAndUpdateDB`, commits, and asserts all keys are absent from key table and absent from deleted table because they have no block data. Failure test uses KEY_NOT_FOUND and confirms keys remain.

State/persistence: Success removes multiple rows from the key table in one response batch. No deleted-table rows are expected for blockless keys. Error response leaves all rows in place.

Dependencies/integration: Exercises bulk response behavior through `OMClientResponse` and request-test key insertion helpers.

Risks/test signals: Does not cover partially failed deletes or block-bearing keys. The misspelled prerequisite method name is harmless but repeated by subclass.
