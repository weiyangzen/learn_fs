<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/OzoneSecretStore.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/OzoneSecretStore.java

Purpose: Persistence adapter for OM delegation-token secret state.

Important APIs/types/functions: `OzoneManagerSecretState<T>` wraps a map from token identifier to renew date. `loadState` creates a state object and populates it through `loadTokens`. `storeToken`, `updateToken`, and `removeToken` write to or delete from `OMMetadataManager.getDelegationTokenTable`. `loadTokens` iterates the full token table.

Control flow: Store/update put the identifier and renew date into the delegation token table. Removal deletes by identifier. Loading seeks the table iterator to first entry and copies each key/value into the in-memory state map, returning a count for logging.

State and persistence behavior: The class persists token renew dates in OM metadata DB. It keeps only an `OMMetadataManager` reference; loaded state is returned to the secret manager.

Dependencies and integration points: Used by `OzoneDelegationTokenSecretManager` at startup and during token mutation/expiration cleanup. Depends on the OM DB table abstraction and token identifier serialization/comparison.

Risks: The generic state type is raw in `loadState`, so compile-time type checking is weak. Full-table loading can be expensive with many tokens. IOException logging includes token details and then rethrows, preserving failure semantics.

Test signals: Tests should verify put/update/delete table calls, complete iterator loading, behavior on table IO failures, and that loaded state keys match serialized/deserialized token identifiers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/OzoneSecretStore.java -->
