<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/compute_member.c -->
# sources/security-integrity/selinux/libselinux/utils/compute_member.c

## Purpose
CLI for computing a member context for polyinstantiation/member relationships.

## Important APIs, Types, And Functions
Calls `security_compute_member()` after validating two contexts and resolving a target class.

## Control Flow
Argument and validation failures use fixed exit codes, then successful computation prints one context.

## State And Persistence Behavior
Read-only policy query.

## Dependencies And Integration Points
Uses standard libselinux validation and stringrep helpers.

## Risks And Test Signals
Test invalid inputs, valid member rules, policy with no member transition, and class mapping behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/compute_member.c -->
