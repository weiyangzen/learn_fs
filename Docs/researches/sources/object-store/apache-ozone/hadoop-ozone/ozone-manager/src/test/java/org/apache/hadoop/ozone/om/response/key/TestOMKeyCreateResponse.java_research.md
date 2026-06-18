# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyCreateResponse.java

Purpose: Tests `OMKeyCreateResponse` for default key creation into the open key table.

Important APIs/types/functions: Uses `OMKeyCreateResponse`, protobuf `CreateKeyResponse`, `getOpenKeyName`, `getVolumeId`, `checkAndUpdateDB`, and `getOpenKeyTable`.

Control flow: The success test builds `OmKeyInfo` and OK `CreateKey` OM response, verifies the open key is absent, adds the response to the batch, commits, and asserts it exists. The error test uses KEY_NOT_FOUND, calls `checkAndUpdateDB`, commits, and asserts the table remains unchanged.

State/persistence: Success persists one open key row in the open key table for the current bucket layout. Error status is a no-op.

Dependencies/integration: Base class provides metadata DB, volume/bucket setup, client ID, key name, and replication config.

Risks/test signals: No block allocation or bucket quota accounting is validated. Main signal is correct success/error handling for open key table writes.
