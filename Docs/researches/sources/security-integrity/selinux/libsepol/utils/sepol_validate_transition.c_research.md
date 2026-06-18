<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/utils/sepol_validate_transition.c -->
# sources/security-integrity/selinux/libsepol/utils/sepol_validate_transition.c

## Purpose

Validates whether a transition from old context to new context by a task context is permitted for a class, including explanatory denial text. The source was read completely for this report (78 lines).

## Important APIs, Types, and Functions

`main()` loads policy, maps old/new/task contexts and class, calls `sepol_validate_transition_reason_buffer(..., SHOW_GRANTED)`, prints `allowed` or `denied`, and returns `7` for denied transitions.

## Control Flow

The utility follows a strict parse/load/convert/validate/print path and frees the reason string before exit.

## State and Persistence Behavior

Only transient SID values and the reason buffer are stored. No persistence.

## Dependencies and Integration Points

Depends on libsepol validation APIs and policydb services.

## Risks and Edge Cases

Risks include interpreting negative errno returns and emitting reason text that may change across libsepol versions.

## Test Signals

Test signal is policy fixture coverage for allowed, denied, invalid context, and invalid class cases.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/utils/sepol_validate_transition.c -->
