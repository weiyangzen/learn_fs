## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneKeyDetails.java

### Purpose
`OzoneKeyDetails` extends `OzoneKey` with block location details, file encryption information, a lazy content stream supplier, and optional generation used for atomic rewrite/conditional commit semantics.

### Important APIs and Types
The constructors accept key metadata plus `List<OzoneKeyLocation>`, `FileEncryptionInfo`, `CheckedSupplier<OzoneInputStream, IOException>`, tags, owner, and optional generation. Getters expose locations, encryption info, generation, and `getContent()`. `hasEtag` and `isEtagEquals` implement ETag checks.

### Control Flow
`getContent()` calls the checked supplier each time it is invoked, allowing content stream creation to be lazy. `isEtagEquals` returns false when the current ETag is missing, treats expected `"*"` as a wildcard when an ETag exists, and otherwise performs string equality.

### State and Persistence Behavior
This is an in-memory detail DTO. The content supplier may create network-backed streams, but this class does not own their lifecycle beyond returning them. Generation and ETag metadata represent server state at lookup time and may become stale.

### Dependencies and Integration Points
It integrates with `OzoneInputStream`, Hadoop `FileEncryptionInfo`, Ratis checked suppliers, and `OzoneConsts.ETAG`. It is returned by `OzoneBucket.getKey` and used by conditional rewrite APIs.

### Risks and Edge Cases
The location list is returned directly, so callers can mutate local representation if the supplied list is mutable. ETag wildcard behavior requires an existing ETag; absent metadata never matches. The content supplier can throw `IOException` and may return a new stream or fail after key state has changed.

### Test Signals
Tests should cover lazy supplier invocation, supplier exception propagation, generation presence/absence, ETag wildcard and missing cases, and preservation of encryption/location details.
