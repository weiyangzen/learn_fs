# sources/sync-backup/syncthing/lib/model/blockpullreorderer.go

## Purpose
Chooses the order in which file blocks are requested during pulling, supporting in-order, random, and standard multi-device distribution strategies.

## Important APIs, Types, and Functions
`blockPullReorderer` exposes `Reorder`. `newBlockPullReorderer` selects by `config.BlockPullOrder`. Implementations are `inOrderBlockPullReorderer`, `randomOrderBlockPullReorderer`, and `standardBlockPullReorderer`. `chunk` splits block slices into approximately equal contiguous parts.

## Control Flow
In-order returns the original slice. Random shuffles the input slice in place. Standard builds a sorted list of all device IDs plus the local ID, records the local device index, splits blocks into one chunk per device, emits the local chunk first when present, then shuffles and appends remaining chunks.

## State and Persistence Behavior
No persistence. Standard reorderer stores local index, device count, and a shuffle function for tests. Random and standard can mutate ordering of provided block slices or returned slices.

## Dependencies and Integration Points
Used by `sendReceiveFolder.handleFile` before copy/pull scheduling. Depends on `config`, `protocol.DeviceID`, `slices`, and Syncthing `rand`.

## Risks
Ordering is a performance and distribution concern, not correctness; however in-place shuffling can surprise callers if they reuse the original slice. Standard mode panics if the local ID is not found after construction, which should be impossible because it appends that ID itself.

## Test Signals
`blockpullreorderer_test.go` verifies chunk boundaries, in-order identity, and deterministic standard ordering with shuffle disabled.
