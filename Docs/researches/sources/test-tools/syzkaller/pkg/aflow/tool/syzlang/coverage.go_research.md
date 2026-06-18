# sources/test-tools/syzkaller/pkg/aflow/tool/syzlang/coverage.go

## Purpose
Provides aflow coverage-inspection tools for executed syz reproducer runs.

## Important APIs, Types, and Functions
Exports `CoverageFiles`, `FileCoverage`, and `Coverage`. `CoverageFilesArgs`/`Result` list covered files from cached execution coverage. `FileCoverageArgs`/`Result` format per-function snippets with covered lines prefixed by `*`.

## Control Flow
Both tools load coverage via `crash.LoadCoverage`. `getCoverageFiles` extracts, sorts, and compacts non-empty frame file paths. `getFileCoverage` validates a local relative filename, groups matching frame lines by function, reads the source file, selects ten lines of context around covered ranges, marks hits, sorts snippets, and returns them.

## State and Persistence Behavior
Reads cached coverage objects and source files. No mutation.

## Dependencies and Integration Points
Depends on `aflow`, `crash.LoadCoverage`, source files under `reproduceState.KernelSrc`, and symbolizer frame data from reproducer execution.

## Risks and Test Signals
Risks include stale cached IDs, unsafe filenames, missing source files, and map iteration ordering; sorting snippets mitigates output nondeterminism. Tests cover file listing and snippet formatting.
