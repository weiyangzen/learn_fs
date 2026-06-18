<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/utils/sepol_compute_member.c -->
# sources/security-integrity/selinux/libsepol/utils/sepol_compute_member.c

## Purpose

Computes a member SID/context for a source context, target context, and target class using the loaded SELinux policy. The source was read completely for this report (67 lines).

## Important APIs, Types, and Functions

`main()` loads policy, converts inputs to SIDs/class, calls `sepol_member_sid()`, converts the output SID back to context with `sepol_sid_to_context()`, prints it, and frees the returned context.

## Control Flow

The control flow is linear validation and computation; any conversion or compute failure prints an error and returns non-zero.

## State and Persistence Behavior

Only transient SIDs and a heap context string are held. The loaded policydb is process global inside libsepol.

## Dependencies and Integration Points

Depends on libsepol services APIs for type/member transition diagnostics.

## Risks and Edge Cases

Risks are poor differentiation between invalid input and policy absence, and reliance on loaded policydb global state.

## Test Signals

Test signal is a known type/member transition producing the expected output context.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/utils/sepol_compute_member.c -->
