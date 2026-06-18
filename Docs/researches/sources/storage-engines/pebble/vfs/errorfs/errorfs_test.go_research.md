<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/errorfs/errorfs_test.go -->
# sources/storage-engines/pebble/vfs/errorfs/errorfs_test.go

## Purpose
Provides datadriven coverage for the `errorfs` DSL parser and string rendering. It verifies that DSL snippets used by other tests parse into the expected injector descriptions or produce stable parse errors.

## Important APIs, Types, and Functions
`TestErrorFS` is the only test entry point. It uses `datadriven.RunTest`, `crstrings.LinesSeq`, `ParseDSL`, and `Injector.String` to process `testdata/errorfs` commands.

## Control Flow
For each datadriven `parse-dsl` command, the test iterates over input lines, parses each line independently, and writes either `parsing err: ...` or the parsed injector's string representation. Unknown commands return a diagnostic string.

## State and Persistence Behavior
The test maintains only a reusable `strings.Builder`; no filesystem state is mutated except reading datadriven fixtures.

## Dependencies and Integration Points
Depends on the parser in `dsl.go`, injector string methods in `errorfs.go` and `latency.go`, and the `datadriven` fixture framework. The output format becomes a regression signal for DSL compatibility.

## Risks and Edge Cases
This file validates parser shape but not actual operation injection against a real wrapped FS. It also does not directly exercise `Counter`, `Toggle`, `Any`, or file-method injection; those are covered indirectly elsewhere.

## Test Signals
The test itself is the signal: expected fixture output catches parser regressions, missing grammar registrations, malformed string rendering, and parse-error changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/errorfs/errorfs_test.go -->
