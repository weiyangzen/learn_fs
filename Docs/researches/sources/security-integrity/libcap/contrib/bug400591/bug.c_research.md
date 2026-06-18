<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug400591/bug.c -->
# sources/security-integrity/libcap/contrib/bug400591/bug.c

## Purpose
Regression test for Debian bug 400591 covering libcap copy, text, and compare APIs.

## Important APIs, Types, And Functions
Uses `cap_get_pid`, `cap_to_text`, `cap_size`, `cap_copy_ext`, `cap_copy_int`, `cap_compare`, `malloc`, and `assert`.

## Control Flow
Reads PID 1 capabilities, converts to text, exports to an external buffer, imports back to a new cap object, converts again, and asserts text and `cap_compare` equality.

## State And Persistence Behavior
No system state is changed. Allocated memory/cap objects are not explicitly freed because process exit follows.

## Dependencies And Integration Points
Links against libcap and reads process capabilities from the kernel.

## Risks And Edge Cases
Assertion-based failure gives limited diagnostics. It assumes PID 1 capabilities are readable and external size is under 1024 bytes.

## Test Signals
Signals are matching text representation and zero comparison after copy ext/int round trip.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug400591/bug.c -->
