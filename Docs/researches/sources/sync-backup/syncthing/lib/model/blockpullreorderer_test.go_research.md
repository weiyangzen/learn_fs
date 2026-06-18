# sources/sync-backup/syncthing/lib/model/blockpullreorderer_test.go

## Purpose
Validates block chunking and reorderer behavior used by the pull pipeline.

## Important APIs, Types, and Functions
Tests target `chunk`, `inOrderBlockPullReorderer.Reorder`, and `standardBlockPullReorderer.Reorder`. `someBlocks` is a small fixture of `protocol.BlockInfo` offsets.

## Control Flow
`Test_chunk` table-checks partition counts including more parts than blocks and nil input. `Test_inOrderBlockPullReorderer_Reorder` checks identity. `Test_standardBlockPullReorderer_Reorder` sorts known device IDs, disables shuffling, and checks the local chunk is moved to the front for different local device positions.

## State and Persistence Behavior
No persistent state. The standard reorderer test mutates the reorderer's `shuffle` field to a no-op for deterministic assertions.

## Dependencies and Integration Points
Uses package-level test device IDs from the model test suite and `protocol.BlockInfo`. Protects `folder_sendrecv.go` block scheduling behavior.

## Risks
Random order behavior is not statistically tested. The tests cover offset ordering, not real block hashes or copy/download side effects.

## Test Signals
Regression signal for even chunking, nil/empty inputs, and stable standard ordering when there are fewer blocks than devices or multiple blocks per selected chunk.
