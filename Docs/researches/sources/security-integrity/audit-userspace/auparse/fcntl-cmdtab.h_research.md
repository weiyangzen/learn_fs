<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/fcntl-cmdtab.h -->
# sources/security-integrity/audit-userspace/auparse/fcntl-cmdtab.h

## Purpose
Provides `fcntl` command number to symbolic-name mappings for interpreting `fcntl*` syscall arguments.

## Important APIs, types, and functions
The `_S` table maps classic commands `F_DUPFD` through `F_GETOWNER_UIDS` and Linux commands from `F_SETLEASE` through read/write hint operations.

## Control flow
Generated lookup code feeds `fcntl_i2s`; `interpret.c:print_fcntl_cmd` parses a hex command and returns the symbol or `unknown-fcntl-command`.

## State and persistence behavior
Compile-time lookup data only.

## Dependencies and integration points
Depends on Linux/uapi fcntl command numbering. Used by syscall argument interpretation for `a1` on `fcntl` variants and downstream `a2` behavior decisions in `print_a2`.

## Risks and test signals
Risks are incomplete coverage for newer commands and architecture-specific numbering. Tests should confirm known command rendering, unknown fallback, and `F_SETOWN`/`F_SETFD` follow-on argument interpretation.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/fcntl-cmdtab.h -->
