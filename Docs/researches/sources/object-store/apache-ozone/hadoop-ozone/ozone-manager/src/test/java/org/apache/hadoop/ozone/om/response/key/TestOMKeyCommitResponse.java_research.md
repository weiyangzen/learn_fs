# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyCommitResponse.java

Purpose: Tests `OMKeyCommitResponse` for committing open keys into the committed key table and handling overwrite cleanup.

Important APIs/types/functions: Uses `OMKeyCommitResponse`, `OMRequestTestUtils.addKeyToTable`, `OmUtils.prepareKeyForDelete`, `RepeatedOmKeyInfo`, `getOzoneDeletePathKey`, `deletedTable`, open/key tables, and `Status.OK`/`KEY_NOT_FOUND`.

Control flow: The success test preloads the open key table, builds an OK commit response with open and final DB keys, adds to batch, commits, and asserts the open row is gone and final key row exists. The no-op test uses KEY_NOT_FOUND and verifies the open row remains. The overwrite test prepares `keysToDelete`, reruns commit, and checks a deleted-table range contains the previous key.

State/persistence: Moves data from open key table to committed key table on success. On overwrite it also writes old key info to `deletedTable` using object-ID-qualified delete paths. Error responses do not mutate.

Dependencies/integration: Integrates base key fixture, OM request test table helpers, delete-key preparation logic, and batch commit.

Risks/test signals: Delete-table validation checks range size and one item, not every delete map detail. HSync/new-open-key branches are passed through constructor parameters but not deeply exercised.
