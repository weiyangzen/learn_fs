# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/file/OMRecoverLeaseResponse.java

Purpose: `OMRecoverLeaseResponse` persists recover-lease state by updating an open key/open file entry, especially for FSO lease recovery flows.

Important APIs and types: It extends `OmKeyResponse`, stores `openKeyName` and `openKeyInfo`, cleans `FILE_TABLE` and `OPEN_FILE_TABLE`, and overrides `getBucketLayout` to FSO.

Control flow: On success, `addToDBBatch` writes `openKeyInfo` to the open key table for the active bucket layout when `openKeyName` is non-null. Failure constructor enforces non-OK status.

State and persistence behavior: It updates open-key/open-file table state and does not modify committed file rows directly.

Dependencies and integration points: It integrates lease recovery request logic, bucket layout routing, and open file cleanup/commit behavior.

Risks and test signals: Tests should cover null open-key no-op, FSO layout routing, failed response no-op, and preservation of lease recovery metadata in `OmKeyInfo`.
