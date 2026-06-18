## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneClientUtils.java

### Purpose
`OzoneClientUtils` collects shared client helpers for link-bucket layout resolution, replication config selection, checksum dispatch, key property checks, list limit clamping, and best-effort snapshot cleanup.

### Important APIs and Types
- `resolveLinkBucketLayout` recursively follows link buckets to the source bucket layout and detects loops with a visited pair set.
- `resolveClientSideReplicationConfig` chooses effective replication for file-system APIs from API short replication, client config, and bucket defaults.
- `getClientConfiguredReplicationConfig` and `validateAndGetClientReplicationConfig` parse replication settings from Ozone configuration and explicit user parameters.
- `getFileChecksumWithCombineMode` builds `OmKeyArgs`, looks up `OmKeyInfo`, selects a checksum helper via `ChecksumHelperFactory`, computes, and returns `FileChecksum`.
- `isKeyErasureCode`, `isKeyEncrypted`, `limitValue`, and `deleteSnapshot` provide focused utility behavior.

### Control Flow
Link resolution checks `bucket.isLink()`, records visited `(volume,bucket)` pairs, fetches source volume/bucket through `ObjectStore`, handles missing source volume/bucket as an orphan link by marking `sourcePathExist=false`, and recurses if the source is also a link. Replication resolution gives EC bucket defaults priority because file-system APIs cannot express EC replication, otherwise honors supported short replication values of ONE or THREE, client defaults, and server-side fallback. Checksum calculation forces latest version locations and sorted datanodes, then delegates to EC or replicated helpers.

### State and Persistence Behavior
The utility class is stateless. It can mutate the passed `OzoneBucket` only in the orphan link case by setting `sourcePathExist` false. `deleteSnapshot` attempts a server-side delete and logs failures without rethrowing.

### Dependencies and Integration Points
It integrates with `ObjectStore`, `OzoneVolume`, `OzoneBucket`, `ClientProtocol`, OM lookup types, HDDS replication config parsing, `OzoneClientConfig.ChecksumCombineMode`, and checksum helper implementations.

### Risks and Edge Cases
Loop detection depends on the caller-supplied visited set and must be initialized correctly. Orphan links return the link bucket's layout, which keeps clients functioning but can mask source deletion until callers inspect `sourcePathExist`. `limitValue` enforces a minimum of two to avoid list-status infinite loops when start keys are echoed. Replication parsing can throw if configuration values are invalid enum names.

### Test Signals
Tests should cover link chains, link loops, orphan link handling, EC bucket default precedence, supported/unsupported short replication values, user-vs-client replication priority, checksum helper selection, encrypted/EC predicates, and `limitValue` max/min clamping.
