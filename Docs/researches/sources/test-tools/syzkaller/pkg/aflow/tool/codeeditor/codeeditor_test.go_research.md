# sources/test-tools/syzkaller/pkg/aflow/tool/codeeditor/codeeditor_test.go

## Purpose
Tests the code editing tool's validation, matching, replacement, and fuzz robustness.

## Important APIs, Types, and Functions
Uses `aflow.TestTool`, `require`, `writeTestFile`, and `FuzzTool`. Test cases call exported `Tool` and private `replace` directly.

## Control Flow
Negative tests assert bad-call messages for traversal, missing files, directories/non-source files, empty snippets, no matches, multiple matches, and no-op edits. Replacement tests create temp source files, invoke the tool, then read files back. `TestReplace` isolates exact and fuzzy line matching. `Fuzz` writes arbitrary bytes and feeds arbitrary snippets through the tool.

## State and Persistence Behavior
All file mutations happen in per-test temp directories. No shared state persists across tests.

## Dependencies and Integration Points
Depends on aflow's test harness, osutil writes, and Go fuzzing. It is the primary regression guard for `codeeditor.go` behavior.

## Risks and Test Signals
The tests signal boundary correctness around newline normalization, fuzzy whitespace handling, ambiguity checks, and panic resistance on arbitrary input.
