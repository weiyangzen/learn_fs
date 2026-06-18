# sources/sync-backup/kopia/snapshot/policy/os_snapshot_policy.go

Purpose: defines policy for OS-level snapshot mechanisms such as Windows Volume Shadow Copy.

Important APIs/types/functions: `OSSnapshotPolicy` contains `VolumeShadowCopy`. `VolumeShadowCopyPolicy` has an optional `OSSnapshotMode`. `OSSnapshotMode` constants are never, always, and when-available, with string constants and helper `NewOSSnapshotMode`, `OrDefault`, `String`, and `mergeOSSnapshotMode`.

Control flow: merge delegates from `OSSnapshotPolicy.Merge` to `VolumeShadowCopyPolicy.Merge`, which fills unset mode from the source policy and records definition source. `String` maps known modes to stable strings and falls back to `"never"`.

State and persistence behavior: policy persists mode values as bytes/numbers unless custom JSON is implemented elsewhere; string method is for presentation. Pointer mode preserves unset versus explicit never.

Dependencies/integration: consumed by snapshot upload code that decides whether to create OS snapshots. Depends on `snapshot.SourceInfo` for definition tracking.

Risks: unknown mode values stringify as `"never"`, which is safe but may hide invalid persisted values. JSON representation should be checked if user-facing config expects strings.

Test signals: `os_snapshot_policy_test.go` covers defaulting and string rendering for all defined modes.
