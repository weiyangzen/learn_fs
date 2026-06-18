<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/validatetrans.c -->
# sources/security-integrity/selinux/libselinux/utils/validatetrans.c

## Purpose
CLI for invoking kernel transition validation.

## Important APIs, Types, And Functions
Validates source, target, and new contexts; resolves class with `string_to_security_class()`; calls `security_validatetrans()`.

## Control Flow
Requires `scontext tcontext tclass newcontext`, prints the return value and current strerror for `errno`, and returns the validation result.

## State And Persistence Behavior
Read-only policy validation query.

## Dependencies And Integration Points
Wrapper for `src/validatetrans.c` and context validation/stringrep APIs.

## Risks And Test Signals
Test valid/invalid transitions, invalid contexts/classes, errno output after success, and shell handling of negative return values.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/validatetrans.c -->
