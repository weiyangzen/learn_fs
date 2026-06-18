# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeySetTimesResponse.java

Purpose: `OMKeySetTimesResponse` persists modification/access time changes for a key in non-FSO layouts.

Important APIs and types: It extends `OmKeyResponse`, stores `OmKeyInfo`, cleans `KEY_TABLE`, and supports an explicit `BucketLayout`.

Control flow: `addToDBBatch` derives the ozone key from volume, bucket, and key name, then writes the updated key info to the key table.

State and persistence behavior: Only key-table metadata changes; block data and bucket accounting are unchanged.

Dependencies and integration points: It is paired with set-times request validation and key-table layout routing.

Risks and test signals: Tests should verify timestamp fields persist, failed response no-op, and bucket layout selection for non-default layouts.
