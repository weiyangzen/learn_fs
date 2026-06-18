# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/PendingKeysDeletion.java

Purpose: `PendingKeysDeletion` is a small data carrier used by OM deletion flows to describe keys whose deleted-table entries are ready to be purged or modified after block reclamation decisions. It separates fully purged keys from `RepeatedOmKeyInfo` records that must remain because not every block or key version is reclaimable.

Important APIs and types: The top-level getters expose `Map<String, PurgedKey> getPurgedKeys()`, `Map<String, RepeatedOmKeyInfo> getKeysToModify()`, and `getNotReclaimableKeyCount()`. Nested `PurgedKey` records the volume, bucket, bucket object ID, `BlockGroup`, delete-table key name, purged bytes, and whether the purged entry represented a committed key.

Control flow: There is no active algorithm in this class. Callers construct it after scanning deletion candidates, then downstream response or cleanup code reads the maps and applies table mutations and accounting updates.

State and persistence behavior: The object itself is transient. Its fields describe persistent OM DB effects: removal from deleted-key tables, modification of repeated deleted-key metadata, and bucket-space accounting through `purgedBytes` and bucket ID. The maps are not defensively copied, so caller ownership matters.

Dependencies and integration points: It depends on `BlockGroup` for SCM block-delete handoff and `RepeatedOmKeyInfo` for OM deleted-key table values. It is part of the bridge between OM metadata cleanup and block reclaim services.

Risks and test signals: Risks are mostly data-contract risks: mutable map aliasing, mismatch between `deleteKeyName` and the map key, and incorrect `isCommittedKey` or bucket ID causing wrong quota updates. Tests should assert mixed reclaimable/non-reclaimable deleted entries, purged-byte accounting, and that not-reclaimable counts preserve remaining repeated-key versions.
