# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeysRenameResponse.java

Purpose: Tests bulk key rename response for legacy/default layout.

Important APIs/types/functions: Uses `OMKeysRenameResponse`, `OmRenameKeys`, `RenameKeysResponse`, `OMRequestTestUtils.addKeyToTable`, and key table DB keys.

Control flow: `createPreRequisities` adds ten keys under `/test/keyN`, mutates each loaded `OmKeyInfo` to target `/test/newKeyN`, and stores a map from source name to updated info in `OmRenameKeys`. Success response commits and verifies old DB keys are absent and new DB keys exist. Failure response with KEY_NOT_FOUND verifies old keys remain and new keys are absent.

State/persistence: Success performs a batch rename of ten key table rows. Error response is a no-op.

Dependencies/integration: Exercises `OmRenameKeys` payload handling and response add/check update path.

Risks/test signals: Only legacy key layout is covered. It does not verify snapshot rename side tables or collisions with existing target keys.
