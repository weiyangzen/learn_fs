<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/selinux_check_securetty_context.c -->
# sources/security-integrity/selinux/libselinux/src/selinux_check_securetty_context.c

## Purpose
Checks whether the type component of a provided context appears in the configured `securetty_types` file.

## Important APIs, Types, And Functions
`selinux_check_securetty_context()` parses `tty_context` with `context_new()`, extracts `context_type_get()`, and scans `selinux_securetty_types_path()`.

## Control Flow
The scanner trims line newlines, skips leading whitespace and blank lines, splits on whitespace, and returns `0` on first type match or `-1` otherwise.

## State And Persistence Behavior
Read-only policy configuration access; no persistent state.

## Dependencies And Integration Points
Uses context parsing and config path helpers. The utility with the same name wraps this API.

## Risks And Test Signals
Test invalid contexts, missing securetty file, blank/whitespace lines, comments treated as tokens, and exact type matches. The function returns the same failure code for no match and read/parse errors.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/selinux_check_securetty_context.c -->
