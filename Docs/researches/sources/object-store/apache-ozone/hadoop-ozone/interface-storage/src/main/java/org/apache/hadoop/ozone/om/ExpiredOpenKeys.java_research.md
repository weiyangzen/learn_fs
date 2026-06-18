# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/ExpiredOpenKeys.java

Purpose: Small aggregation container for expired open keys discovered by OM cleanup logic.

Important APIs/types/functions: Exposes `getOpenKeyBuckets()` for non-hsync open keys and `getHsyncKeys()` for hsync-ed keys. Package-private `addOpenKey(OmKeyInfo, String)` groups open key DB names by volume/bucket into `OpenKeyBucket.Builder`. Package-private `addHsyncKey(KeyArgs.Builder, long)` creates `CommitKeyRequest.Builder` entries for hsync cleanup.

Control flow, state, and persistence: Maintains in-memory `Map<String, OpenKeyBucket.Builder>` keyed by `volume/bucket` and a list of `CommitKeyRequest.Builder`. It does not persist itself; callers convert builders into protobuf requests such as `DeleteOpenKeysRequest` or commit-related cleanup flows.

Dependencies and integration points: Uses `OmKeyInfo` for volume/bucket lookup, `OM_KEY_PREFIX` for grouping key construction, and generated `OpenKeyBucket`, `OpenKey`, `KeyArgs`, and `CommitKeyRequest` messages from `OmClientProtocol.proto`.

Risks: The map key is string-concatenated with `OM_KEY_PREFIX`; any inconsistency with OM DB key conventions can group keys incorrectly. The class is mutable and not synchronized, so it should remain request/local-thread scoped. Builders expose mutable protobuf state to callers.

Test signals: No direct test in this subset. Indirect signals should come from OM open-key expiration and hsync cleanup tests.
