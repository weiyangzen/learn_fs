<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug400591/Makefile -->
# sources/security-integrity/libcap/contrib/bug400591/Makefile

## Purpose
Build recipe for bug400591 regression test around libcap external/internal capability copy APIs.

## Important APIs, Types, And Functions
Target `bug` builds `bug.c` statically against in-tree libcap and runs it. `clean` removes objects and binary.

## Control Flow
Builds `../../libcap`, compiles with include/library paths, then executes `./bug` as part of the build target.

## State And Persistence Behavior
Creates a static test binary; clean removes it.

## Dependencies And Integration Points
Depends on C compiler and in-tree libcap static library/header.

## Risks And Edge Cases
Static linking can fail if required static dependencies are unavailable. Running during build means compilation success is not enough.

## Test Signals
Signals are no assertion failures from `bug`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug400591/Makefile -->
