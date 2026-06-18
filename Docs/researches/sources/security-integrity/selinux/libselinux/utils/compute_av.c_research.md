<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/compute_av.c -->
# sources/security-integrity/selinux/libselinux/utils/compute_av.c

## Purpose
CLI for computing access-vector decisions between two contexts and a target class.

## Important APIs, Types, And Functions
`main()` validates source/target contexts, resolves class with `string_to_security_class()`, calls `security_compute_av()`, and prints allowed, decided, undecided, auditallow, auditdeny, and dontaudit vectors with `print_access_vector()`.

## Control Flow
Invalid arguments, contexts, class, or compute failures map to distinct exit codes.

## State And Persistence Behavior
Read-only policy query; no state changes.

## Dependencies And Integration Points
Exercises context validation, stringrep, kernel policy computation, and access-vector printing.

## Risks And Test Signals
Tests should cover invalid context/class exits, valid decisions, unknown permissions in print output, and SELinux disabled/missing selinuxfs behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/compute_av.c -->
