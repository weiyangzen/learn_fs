# sources/storage-engines/pebble/internal/treesteps/tree_steps_off.go

## Purpose
This file provides the no-op implementation of treesteps for builds without the `invariants` tag. It allows instrumentation calls to remain in production code with minimal overhead.

## Important APIs, Types, and Functions
It defines `Enabled = false`, stub `RecordingOption`, `MaxTreeDepth`, `MaxOpDepth`, `StartRecording`, `NodeUpdated`, `Node`, `NodeInfo`, `NodeInfof`, `AddPropf`, `AddChildren`, `Recording.Finish`, `IsRecording`, `Op`, `StartOpf`, `Updatef`, `UpdateLastOpf`, `Finishf`, and `TreeToString`. Most return zero values, nil, or no-op.

## Control Flow and State
There is no real recording state. `StartRecording` returns nil, operation methods tolerate nil receivers by doing nothing, and `TreeToString` returns a fixed unsupported message.

## Dependencies and Integration
It is selected by `//go:build !invariants` and imports Cockroach errors anonymously, likely to keep package dependencies aligned or satisfy build constraints. It must mirror the public API of the invariants implementation.

## Risks and Edge Cases
Callers must tolerate nil recordings and nil operations in non-invariants builds. Any API added to the on implementation must be mirrored here to avoid build breaks. `Recording.Finish` on a nil recording is not used; `StartRecording` returns nil, so callers normally guard or assign only in tests.

## Test Signals
`tree_steps_test.go` skips when `Enabled` is false, so this file is mainly validated by ordinary non-invariants builds compiling successfully.
