<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/utils/sepol_compute_av.c -->
# sources/security-integrity/selinux/libsepol/utils/sepol_compute_av.c

## Purpose

Diagnostic wrapper for `sepol_compute_av()` that prints allowed, decided, auditallow, and auditdeny permission sets for a source/target/class request. The source was read completely for this report (71 lines).

## Important APIs, Types, and Functions

`main()` loads policy, converts contexts and class, calls `sepol_compute_av()`, and formats each returned access-vector field with `sepol_av_perm_to_string()`.

## Control Flow

Straight-line CLI flow: validate arity, load policy, convert identifiers, compute, switch on return code, print human-readable output.

## State and Persistence Behavior

State is process-local plus libsepol loaded policydb globals. No persistence.

## Dependencies and Integration Points

Depends on libsepol services and sepol public APIs; built with other libsepol utilities.

## Risks and Edge Cases

Risks are mainly diagnostic accuracy for invalid classes/contexts and ensuring errno-style returns are interpreted correctly.

## Test Signals

Useful smoke tests run known allow and deny examples and compare printed AV fields.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/utils/sepol_compute_av.c -->
