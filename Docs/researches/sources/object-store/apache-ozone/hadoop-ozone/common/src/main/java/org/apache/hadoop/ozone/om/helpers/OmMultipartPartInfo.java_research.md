# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartPartInfo.java

Purpose: Persisted metadata for one multipart upload part, used by the schema-version-1 multipart parts table and conversion from committed part `OmKeyInfo`.

Important APIs/types/functions: `CODEC` delegates to `MultipartPartInfo`. Builder sets part name/number, size, modification time, object/update IDs, key-location groups, ETag, encryption info, and checksum. `getProto`, `getFromProto`, and `from(partName, partNumber, OmKeyInfo)` are primary conversion APIs.

Control flow and state: `getProto` validates required fields: nonblank part name and ETag, positive part number and modification time, nonnegative size, and nonempty key locations. Parsing validates required proto fields and logs warnings for missing object/update IDs while still reading default values. Only the first key-location group is serialized for the part.

State and persistence behavior: Stored as protobuf in the multipart parts table. It persists block locations with pipeline omitted, object/update IDs, encryption info, checksum, size, time, and ETag.

Dependencies and integration points: Used by MPU commit/list/complete in newer schema. Depends on `OmKeyInfo`, `OmKeyLocationInfoGroup`, `OMPBHelper`, `ClientVersion`, and Ozone ETag metadata.

Risks: `from` requires the source `OmKeyInfo` to have an ETag or builder validation fails. Multiple key-location groups are reduced to the first during serialization. Missing object/update IDs are warning-only, preserving compatibility but risking weak identity data.

Test signals: Codec round trips, required-field validation, conversion from `OmKeyInfo`, encrypted/checksummed part persistence, object/update ID warnings, and part-number/ETag validation.
