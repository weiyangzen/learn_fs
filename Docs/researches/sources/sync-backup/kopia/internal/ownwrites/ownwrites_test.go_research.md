# sources/sync-backup/kopia/internal/ownwrites/ownwrites_test.go

Purpose: validates own-writes consistency behavior with fake time and eventually consistent storage.

Important APIs/types/functions: `TestOwnWrites`, fake time sources, `blobtesting.NewEventuallyConsistentStorage`, and `NewWrapper`.

Control flow: seeds settled data, writes cached and uncached prefixes, asserts cache marker creation, checks that wrapper lists fresh writes before provider consistency catches up, deletes a blob and verifies deletion hiding, then advances cache time to trigger marker sweep.

State and persistence behavior: all state lives in in-memory map storages and fake clocks.

Dependencies and integration points: exercises the real `CacheStorage` implementation through the `blob.Storage` interface.

Risks and test signals: strong coverage for add/delete marker semantics; does not cover cache-storage failures or concurrent listing/writes.
