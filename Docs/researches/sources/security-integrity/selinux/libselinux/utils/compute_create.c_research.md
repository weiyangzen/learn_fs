<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/compute_create.c -->
# sources/security-integrity/selinux/libselinux/utils/compute_create.c

## Purpose
CLI for computing the default create context for a source context, target context, class, and optional object name.

## Important APIs, Types, And Functions
Uses `security_check_context()`, `string_to_security_class()`, and `security_compute_create_name()`.

## Control Flow
Requires three or four operands after the program name, validates inputs, calls compute, prints the returned context, and frees it.

## State And Persistence Behavior
Read-only policy query.

## Dependencies And Integration Points
Integrates with class string resolution and name-based type transition policy.

## Risks And Test Signals
Test named and unnamed creates, invalid contexts/classes, no transition errors, and object names with unusual characters.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/compute_create.c -->
