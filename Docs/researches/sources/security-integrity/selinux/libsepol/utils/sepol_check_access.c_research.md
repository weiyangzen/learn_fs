<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/utils/sepol_check_access.c -->
# sources/security-integrity/selinux/libsepol/utils/sepol_check_access.c

## Purpose

Policy diagnostic utility that answers whether a source context has one or more permissions to a target context/class and reports denial reasons. The source was read completely for this report (139 lines).

## Important APIs, Types, and Functions

`main()` loads a policy, maps source/target contexts to SIDs, maps a class and comma-separated permission list to an access vector, then calls `sepol_compute_av_reason_buffer()` and prints allowed or denial reasons.

## Control Flow

After input validation, permission parsing loops over comma-delimited names, accumulates an access vector, computes an AV decision, and exits `0` for fully allowed or `7` for denied.

## State and Persistence Behavior

Uses libsepol global policydb state and a heap `reason_buf` returned by libsepol. No persistent state.

## Dependencies and Integration Points

Depends on libsepol services APIs for policy loading, context/SID conversion, permission mapping, AV computation, and reason formatting.

## Risks and Edge Cases

One subtle risk is access-vector accumulation: the local `av` variable must be initialized before OR-style permission construction by the libsepol API path. CLI parsing also mutates only temporary permission slices.

## Test Signals

Signals include allowed/denied exit codes, reason categories for TE/constraint/RBAC/bounds, and constraint reason text when available.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/utils/sepol_check_access.c -->
