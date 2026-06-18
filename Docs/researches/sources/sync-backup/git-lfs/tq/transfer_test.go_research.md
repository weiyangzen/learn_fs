# sources/sync-backup/git-lfs/tq/transfer_test.go

Purpose: tests adapter registration, fallback, override, and basic-only listing behavior through the manifest.

Important APIs/types/functions: `testAdapter`, `newTestAdapter`, `newRenamedTestAdapter`, `TestBasicAdapterExists`, `TestAdapterRegAndOverride`, and `TestAdapterRegButBasicOnly`.

Control flow: creates manifests, queries adapter lists and specific adapters, registers test factories for upload/download, overrides them, and asserts custom flags plus fallback-to-basic behavior.

State and persistence: in-memory manifest state only.

Dependencies and integration points: validates manifest registry used by transfer queue adapter selection.

Risks: one assertion in `TestBasicAdapterExists` compares upload adapters using `dls` rather than `uls`, which could mask upload-list mismatch.

Test signals: strong registry behavior coverage despite the noted assertion issue.
