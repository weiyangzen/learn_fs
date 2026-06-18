# sources/test-tools/syzkaller/pkg/aflow/tool/toolkit/testdata/toolkit_standalone_test.c

## Purpose
Minimal compile-only style smoke test proving `race_toolkit.h` can be included by a standalone C file.

## Important APIs, Types, and Functions
Includes `../race_toolkit.h` and defines `main` returning zero.

## Control Flow
No runtime logic beyond process start and return.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
Built by `toolkit_test.go` with the same compiler flags as other toolkit testdata.

## Risks and Test Signals
Signals header self-containment. It does not exercise macros or Linux runtime APIs.
