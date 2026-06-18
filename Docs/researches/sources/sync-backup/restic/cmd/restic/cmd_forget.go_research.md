# sources/sync-backup/restic/cmd/restic/cmd_forget.go

Purpose: implements `restic forget`, removing snapshot objects explicitly or according to retention policies, and optionally running prune afterward.

Important APIs/types/functions: `ForgetPolicyCount` parses keep counts including `unlimited`; `ForgetOptions` stores count, duration, tag, safety, snapshot filter, grouping, dry-run, and prune options. `verifyForgetOptions` rejects invalid negative counts/durations. `runForget` applies filters/policies and removes snapshots. `ForgetGroup`, `KeepReason`, `asJSONSnapshots`, `asJSONKeeps`, and `printJSONForget` implement JSON output.

Control flow: validates forget and prune options, rejects unsafe `--no-lock` except dry-run, opens an exclusive lock, loads filtered snapshots, either removes explicitly named snapshots or groups snapshots and applies `data.ExpirePolicy`, enforces safety rails against deleting an entire group unless explicitly allowed with filters, removes selected snapshot files in parallel unless dry-run, emits JSON groups, returns a distinct error if any removals failed, and invokes prune when requested.

State/persistence: deletes snapshot files from the repository and may trigger prune to remove unreferenced data. Dry-run avoids deletion. Exclusive locking protects repository mutation.

Dependencies/integration: snapshot filters/grouping/policy logic in `internal/data`, repository remove primitives, prune command, UI progress, and JSON snapshot wrappers.

Risks/test signals: retention policy safety is critical; empty policy plus unsafe remove-all is constrained. Failed partial deletes return `ErrFailedToRemoveOneOrMoreSnapshots`. Tests cover policy count parsing, negative values, host defaulting, and safety-net integration.
