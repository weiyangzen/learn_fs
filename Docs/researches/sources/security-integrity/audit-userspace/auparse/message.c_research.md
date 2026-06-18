<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/message.c -->
# sources/security-integrity/audit-userspace/auparse/message.c

## Purpose
Implements auparse internal message routing to stderr, syslog, or quiet mode.

## Important APIs, types, and functions
`set_aumessage_mode` stores `message_t` and debug settings on `auparse_state_t`. `audit_msg` checks quiet/debug suppression, then emits formatted output through `vsyslog` or `vfprintf(stderr)`.

## Control flow
Message mode is set on parser state, then every `audit_msg` call first exits for quiet mode or disabled debug messages. Otherwise it initializes a `va_list`, routes to syslog or stderr, appends a newline for stderr, and ends the varargs.

## State and persistence behavior
State is limited to two fields in parser state. Messages may persist externally only if syslog captures them.

## Dependencies and integration points
Depends on `libaudit.h`, `private.h`, and `internal.h`. It backs private aliases `audit_msg`/`set_aumessage_mode` used throughout auparse code.

## Risks and test signals
Risks are null parser pointers, format-string misuse by callers, and debug messages leaking when disabled. Tests should cover quiet suppression, stderr output, syslog mode via mocks if available, and debug filtering.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/message.c -->
