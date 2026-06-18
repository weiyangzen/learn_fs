<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/private.h -->
# sources/security-integrity/audit-userspace/auparse/private.h

## Purpose
Declares private auparse messaging aliases and hidden message-mode functions.

## Important APIs, types, and functions
Defines `audit_msg` as `auparse_msg` and `set_aumessage_mode` as `set_aup_message_mode`. Declares `auparse_msg` with printf-format checking and `set_aup_message_mode`.

## Control flow
Callers use the audit-style aliases; implementation in `message.c` routes messages according to parser state.

## State and persistence behavior
No state in the header; message mode/debug fields live in `auparse_state_t`.

## Dependencies and integration points
Depends on public `auparse.h`, common definitions, and DSO visibility. Used by internal auparse modules needing diagnostics without exporting generic symbol names.

## Risks and test signals
Risks are macro alias confusion and mismatched format strings. Compile-time format warnings and mode-routing tests in `message.c` are the main signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/private.h -->
