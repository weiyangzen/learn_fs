# sources/user-network-fs/rclone/backend/combine/combine_internal_test.go

## Purpose
This file unit-tests `adjustment`, the path translation primitive that maps upstream-relative paths into combined paths and combined paths back into upstream-relative paths. Correctness here is central because most combine backend operations delegate based on these transformations.

## Important APIs, types, and functions
`TestAdjustmentDo` covers `newAdjustment(...).do`, which maps an upstream path into the combine view. `TestAdjustmentUndo` covers `newAdjustment(...).undo`, which maps a combine path into the upstream namespace. The tests use `assert.Equal` from `stretchr/testify`.

## Control flow
Each test iterates table-driven cases with `root`, `mountpoint`, `in`, expected `want`, and expected error. `do` cases validate empty root prefixing, root equal to mountpoint, nested roots that strip a shared prefix, and `errNotUnderRoot` for inputs outside the combined root. `undo` cases validate the reverse mapping from combine-visible paths back to upstream paths and error behavior when the effective absolute path does not fall under the mountpoint.

## State and persistence behavior
There is no persistent state. Each case creates a fresh `adjustment` value and checks pure string transformations.

## Dependencies and integration points
The tests are in package `combine`, not `combine_test`, so they can access unexported `newAdjustment` and `errNotUnderRoot`. They directly protect the internal routing logic used by `findUpstream`, listing wrappers, `Object.Remote`, and operations that delegate to upstream paths.

## Risks and edge cases
The tests cover representative root/mountpoint relationships but not empty mountpoint rejection, leading slashes, path cleaning behavior from `join`, root equal to input path returning empty string, or mountpoints with characters that might interact with `path.Join`. They also do not cover nondeterministic map iteration in `findUpstream`.

## Test signals
These are fast deterministic unit tests that isolate the highest-risk string mapping logic. They complement the broader `fstests` integration coverage in `combine_test.go`.
