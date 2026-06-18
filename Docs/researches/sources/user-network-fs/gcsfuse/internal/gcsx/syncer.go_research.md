# sources/user-network-fs/gcsfuse/internal/gcsx/syncer.go

## Scope

This file defines and implements `Syncer`, the write-back component that syncs a mutable local `TempFile` to a GCS object generation.

## Purpose

`Syncer` avoids unnecessary uploads when local content is unchanged, writes new local files fully, and can optimize append-only changes by composing a temporary appended blob with the original object when safe and supported.

## Important APIs, Types, And Functions

- `Syncer` interface exposes `SyncObject`.
- `NewSyncer` chooses a full-object creator and, unless rapid writes are enabled, a compose creator.
- `fullObjectCreator.Create` builds a `gcs.CreateObjectRequest` from source metadata and uploads full contents.
- `objectCreator` abstracts full and compose upload paths.
- `newSyncer` wires thresholds, retry/timeout settings, and creators.
- `syncer.SyncObject` implements dirty-state decisions and upload/compose selection.

## Control Flow

`SyncObject` stats the temp file. If there is no source object, it seeks to the beginning and uploads the full local file. For existing objects, it validates dirty threshold against finalized source size, returns early if `Mtime` is nil, and for finalized objects returns early if size and dirty threshold match source size. Otherwise, it composes only when compose is available, source size meets threshold, dirty threshold equals source size, and component count is below the GCS max; otherwise it seeks to the beginning and uploads the full object.

## State And Persistence Behavior

The syncer stores configuration thresholds and creator dependencies only. Durable effects are new GCS object generations, and possibly temporary compose blobs managed by the compose creator. It mutates the temp file's current offset via `Seek` before handing it to creators.

## Dependencies And Integration Points

It depends on `TempFile.Stat`, `TempFile.Seek`, GCS object metadata, `gcs.NewCreateObjectRequest`, bucket `CreateObject`, compose object creator, bucket type rapid-write support, component count limits, and chunk retry/transfer timeout settings.

## Risks And Maintenance Notes

Dirty-threshold and unfinalized-object logic is subtle. For unfinalized zonal/rapid objects, size metadata may be stale, so the code bypasses one unchanged-content shortcut to avoid silently skipping truncations. Compose is disabled for rapid-write buckets. Any changes to `TempFile.Stat` semantics can cause missed uploads or redundant uploads. Error wrapping identifies whether failures occurred during stat, seek, create request, or create execution.

## Test Signals

This subset does not include `syncer_test.go`, but the production file has comments documenting expected cases: unmodified temp files return nil object, local-only files upload fully, append-only large finalized objects can use compose, and dirty or unsupported cases upload fully.
