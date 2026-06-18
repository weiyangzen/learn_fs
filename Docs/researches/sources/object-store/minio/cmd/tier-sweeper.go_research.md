# sources/object-store/minio/cmd/tier-sweeper.go

Purpose: decides when a local object mutation should enqueue deletion of a corresponding remote-tier object. It prevents transitioned remote objects from being orphaned after overwrites/deletes while respecting bucket versioning semantics.

Important APIs and types: `objSweeper` tracks bucket/object, requested version ID, bucket versioning state, transition status/tier/version/name, and helper methods `WithVersion`, `WithVersioning`, `GetOpts`, `SetTransitionState`, `shouldRemoveRemoteObject`, and `Sweep`. `jentry` is the tier deletion journal entry. `deleteObjectFromRemoteTier` resolves a `WarmBackend` and calls `Remove`.

Control flow: callers create a sweeper before an operation, use `GetOpts` to fetch the affected object version, call `SetTransitionState` from object info when transition metadata exists, perform the local operation, then call `Sweep`. `shouldRemoveRemoteObject` first requires lifecycle transition status `TransitionComplete`. It then deletes remote data if bucket versioning is disabled, if versioning is suspended, or if versioning is enabled and a specific version ID was targeted. Versioning-enabled deletes without a version ID only add a delete marker and do not remove remote data.

State and persistence: `Sweep` enqueues into `globalExpiryState` rather than synchronously deleting. Actual remote removal is journal-driven. The sweeper itself is per-operation transient state.

Dependencies and integration points: depends on lifecycle transition constants, `ObjectOptions`, `TransitionedObject`, `nullVersionID`, `globalExpiryState`, `globalTierConfigMgr`, and `WarmBackend.Remove`. It integrates object APIs with ILM tier cleanup.

Risks: incorrect versioning decisions can delete remote data still referenced by an older version or leak remote data after overwrite/delete. The suspended-bucket null-version handling in `GetOpts` is especially important for matching the object that will be overwritten. Remote driver lookup failures surface when journal processing calls `deleteObjectFromRemoteTier`.

Test signals: no tests in this file. Good coverage would enumerate disabled/suspended/enabled versioning with and without explicit version IDs, incomplete transition state, and journal entry fields.
