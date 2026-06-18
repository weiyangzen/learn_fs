
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/util/OMMultipartUploadUtils.java

Purpose: Shared utility methods for multipart upload ID generation, DB-key parsing, layout-aware open-key construction, and multipart flag checks.

Important APIs and types: Static utility class; uses `UUIDv7.randomUUID`, `UniqueId.next`, `OMMetadataManager.getMultipartKey`/`getMultipartKeyFSO`, `BucketLayout`, `OmKeyInfo`, `OM_KEY_PREFIX`, and `StringUtils`.

Control flow: `getMultipartUploadId` creates a UUIDv7 plus unique numeric suffix. `getUploadIdFromDbKey` splits a DB key on `/`, requires enough path components, validates the suffix shape as UUID plus unique ID, and returns it or null. `getMultipartOpenKey` dispatches to FSO or object-store key generation. `isMultipartKeySet` checks latest version locations and its multipart flag.

State and persistence behavior: No persistence; helpers derive IDs and keys used by request handlers that persist multipart state.

Dependencies and integration points: Used by multipart initiate/commit/complete/abort paths across regular and FSO layouts.

Risks: Upload ID parsing is shape-based and assumes six hyphen-delimited pieces. Key splitting depends on `OM_KEY_PREFIX`. Tests should cover malformed DB keys, FSO/non-FSO open-key generation, null latest locations, and UUIDv7 ID uniqueness/format.
