# sources/sync-backup/kopia/snapshot/snapshotfs/snapshot_verifier.go

Purpose: verifies snapshot filesystem objects and optional backing blob presence in parallel, with progress statistics and bounded error reporting.

Important APIs/types/functions: `Verifier`, `VerifierStats`, `VerifierOptions`, `VerifierResult`, `AddToExpectedTotals`, `VerifyFile`, `verifyObject`, `readEntireObject`, `InParallel`, and `NewVerifier`.

Control flow: `InParallel` creates a `TreeWalker`, starts file verification workers, lets the caller enqueue roots through the walker, closes the file queue, waits, then returns accumulated stats and errors. Directories count as processed immediately; files are queued for object verification, optional blob-map checking, and probabilistic full reads.

State and persistence: read-only repository access. Stats live on the verifier instance and are not reset by `InParallel`; callers needing isolated stats should create a new verifier.

Dependencies and integration points: integrates with `TreeWalker`, repository `VerifyObject`, `ContentInfo`, `OpenObject`, blob maps, JSON stats logging, and CLI verification commands.

Risks and test signals: random read sampling depends on `VerifyFilesPercent`. Blob-map mode detects missing pack blobs before full reads. `MaxErrors` limits stored errors and worker processing.
