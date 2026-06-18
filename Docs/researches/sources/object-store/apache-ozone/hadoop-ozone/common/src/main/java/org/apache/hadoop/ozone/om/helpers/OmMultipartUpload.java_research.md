# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartUpload.java

Purpose: Listing/identity DTO for one initialized multipart upload.

Important APIs/types/functions: Constructors store volume, bucket, key, upload ID, optional creation time, and optional replication config. `from(String dbKey)` parses legacy DB key format. `getDbKey` and static `getDbKey` build `/volume/bucket/key/uploadId` keys. Equality/hash are based on upload ID.

Control flow and state: `from` splits the key on `/`, validates at least five segments, derives upload ID from the last segment, volume/bucket from leading segments, and reconstructs key name by substring to preserve embedded separators.

State and persistence behavior: Represents rows from multipart upload tables and list responses. DB key format is string-based with slash separators.

Dependencies and integration points: Used by list multipart uploads and legacy multipart DB key handling. Depends on `ReplicationConfig`.

Risks: Equality by upload ID ignores volume/bucket/key; uniqueness must be global for this to be safe. Parsing assumes a leading slash and enough segments; malformed keys throw.

Test signals: DB key build/parse round trips with keys containing slashes, creation time/replication config propagation, equality semantics, and malformed key rejection.
