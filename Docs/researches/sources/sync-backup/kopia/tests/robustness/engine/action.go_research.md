
# sources/sync-backup/kopia/tests/robustness/engine/action.go

## Purpose
Defines the robustness engine action system: executable action keys, weighted random selection, action repetition, logging/stat accounting, no-op handling, no-space recovery, and concrete snapshot/file/GC actions.

## Important APIs, Types, And Functions
- `ExecAction` executes a named action, repeats it according to `repeat-action`, updates stats/logs, and treats `robustness.ErrNoOp` specially.
- `RandomAction` picks an action using control weights and runs recovery handling.
- `CheckErrRecovery` recovers from no-space errors by deleting data, then restoring a snapshot into the data directory.
- Action keys include snapshot, restore random snapshot, delete random snapshot, write random files, delete random subdirectory, delete files, restore into data dir, and run GC.
- Concrete action functions call `Engine.Checker`, `FileWriter`, or `TestRepo`.
- `defaultActionControls`, `pickActionWeighted`, `errIsNotEnoughSpace`, and `getSnapIDOptOrRandLive` support weighted random execution and option parsing.

## Control Flow
Random actions read weights from `ActionOpts[ActionControlActionKey]`, pick a key using reservoir-style weighted selection, execute the action, and then run recovery logic if needed. Concrete actions populate log command options with snapshot IDs, paths, and file-writer outputs.

## State And Persistence Behavior
Actions mutate the data directory, snapshot repository, metadata repository via `Checker`, engine logs, and stats counters. No-space recovery can delete all data-directory contents and restore from a live snapshot.

## Dependencies And Integration Points
Uses `robustness` interfaces, `checker`, file writer APIs, engine stats/log helpers, and option names from fio/file-writer packages.

## Risks And Edge Cases
`ExecAction` indexes `actions[actionKey]` without validating presence; an unknown key will call a nil function and panic. Weighted picking depends on map iteration randomness but produces correct probabilities statistically. No-space detection includes string matching on `"no space left on device"`.

## Test Signals
Central behavioral layer for robustness random tests and recovery-on-error scenarios.
