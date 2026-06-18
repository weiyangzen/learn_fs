# sources/sync-backup/kopia/repo/blob/beforeop/beforeop_test.go

Purpose: validates `beforeop` wrapper callback behavior.

Important APIs/types/functions: `TestBeforeOpStorageNegative`, `TestBeforeOpStoragePositive`, `NewWrapper`, `NewUniformWrapper`, and blob operation methods against a test storage.

Control flow: negative tests configure callbacks that return errors and assert the wrapped storage operation is not allowed to proceed. Positive tests configure callbacks that record invocation and allow operations through, checking both operation-specific and uniform callback paths.

State and persistence behavior: tests use local/mock storage state and callback counters/errors. No external persistence is involved.

Dependencies/integration points: exercises wrapper composition with Kopia's blob interface. Risks/test gaps include no coverage for `onPutBlob` mutating options, no concurrent callback behavior, and no list/close behavior because those methods are not wrapped. The tests are useful to ensure pre-operation failures remain fail-fast.
