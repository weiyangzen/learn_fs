# sources/user-network-fs/rclone/fs/list/helpers_test.go

## Purpose
`helpers_test.go` verifies the batching semantics of `list.Helper` and the `WithListP` adapter from paged callback listing to accumulated directory entries.

## Important APIs, types, and functions
Tests target `NewHelper`, `Helper.Add`, `Helper.Flush`, and `WithListP`. `mockListPfs` implements `fs.ListPer` and emits entries in two-entry pages, optionally returning an error after a configured count.

## Control flow
Helper tests construct callbacks that record invocation, add mock objects, and assert whether buffered entries remain or callbacks fired. `WithListP` tests build 26 mock entries, run normal and error cases, and compare returned slices to the expected full or partial prefix.

## State and persistence behavior
All state is in-memory test slices and booleans. No files or remote state are used.

## Dependencies and integration points
The tests use `mockobject`, `fs.ListPer`, context, testify, and errors. They protect helper behavior used by recursive backend listing implementations and paged listing adapters.

## Risks and edge cases
The threshold is fixed at 100, so tests assert exact behavior at the boundary. The mock paging loop uses `entries[:2]` while advancing by two and assumes an even count, matching the test's 26 entries.

## Test signals
Coverage is focused and useful: constructor callback identity, ignored nil entries, callback batching, buffer clearing, final flush, page aggregation, and error propagation with partial results.

Source-read signal: reviewed complete local file (145 lines). Types observed: `mockListPfs`. Functions/methods observed: `mockCallback`, `TestNewListRHelper`, `TestListRHelperAdd`, `TestListRHelperSend`, `TestListRHelperFlush`, `ListP`, `TestListWithListP`.
