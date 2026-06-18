# sources/test-tools/syzkaller/pkg/aflow/tool/codesearcher/codesearcher_test.go

## Purpose
Tests the struct-layout aflow wrapper against a small prebuilt codesearch test index.

## Important APIs, Types, and Functions
`TestStructLayout`, `TestStructLayoutNonExistent`, and `createIndex` use `codesearch.NewTestIndex` and `aflow.TestTool`.

## Control Flow
The positive test asks for `struct_in_c_file` and expects fields with bit offsets and sizes. The negative test asks for a missing name and expects the tool error.

## State and Persistence Behavior
Uses testdata through a temporary test index wrapper; no persistent writes.

## Dependencies and Integration Points
Depends on aflow's tool harness and `pkg/codesearch` test index fixtures.

## Risks and Test Signals
Good signal for wrapper shape and error propagation, but it does not cover index preparation, comments, source, or reference search.
