# sources/sync-backup/git-lfs/tq/errors.go

Purpose: typed errors for missing or corrupt local LFS objects.

Important APIs/types/functions: `MalformedObjectError`, `newObjectMissingError`, `newCorruptObjectError`, `Missing`, `Corrupt`, and `Error`.

Control flow: constructors set `missing`; methods expose missing/corrupt classification and format translated messages.

State and persistence: immutable error values only.

Dependencies and integration points: `TransferQueue.partitionTransfers` and upload batch checks use these errors for missing/corrupt upload objects.

Risks: type assertions are needed to inspect classification; both constructors return `error`, hiding concrete type unless asserted.

Test signals: `errors_test.go` verifies fields and classification methods.
