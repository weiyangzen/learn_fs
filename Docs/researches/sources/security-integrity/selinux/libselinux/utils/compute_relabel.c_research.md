<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/compute_relabel.c -->
# sources/security-integrity/selinux/libselinux/utils/compute_relabel.c

## Purpose
CLI for computing the context allowed/selected for a relabel operation.

## Important APIs, Types, And Functions
Validates source/target contexts, resolves class, calls `security_compute_relabel()`, prints and frees the result.

## Control Flow
Mirrors the `compute_member` pattern with distinct exit codes for bad inputs or compute failure.

## State And Persistence Behavior
Read-only policy query; no xattrs are changed.

## Dependencies And Integration Points
Useful for testing relabel policy without invoking `restorecon` or `setfilecon`.

## Risks And Test Signals
Test valid relabel rules, invalid contexts, invalid classes, and kernel query errors.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/compute_relabel.c -->
