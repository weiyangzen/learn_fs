<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/filewriter.go -->
# sources/sync-backup/kopia/tests/robustness/filewriter.go

This file defines the `robustness.FileWriter` interface used by the engine to mutate a source data tree. The interface exposes `DataDirectory`, `WriteRandomFiles`, `DeleteRandomSubdirectory`, `DeleteDirectoryContents`, and `DeleteEverything`, all context-aware where engine actions need cancellation/logging propagation.

Control flow is implemented by concrete adapters such as `fiofilewriter.FileWriter` and multiclient wrappers. Returned option maps are important because the engine logs effective randomized choices, enabling reproduction and audit of actions.

There is no state here, but the contract defines stateful behavior for file-system mutation. Risks are interface semantic drift: implementers must translate "no useful mutation" to `ErrNoOp`, must avoid deleting outside their data root, and must return meaningful effective options. Test signals come from FIO workload tests and robustness engine action tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/filewriter.go -->
