<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/mounttab.h -->
# sources/security-integrity/audit-userspace/auparse/mounttab.h

## Purpose
Maps mount flag bits to names for `mount`, `fsmount`, and related audit interpretation.

## Important APIs, types, and functions
The `_S` table includes common `MS_*` flags and newer literal bit entries such as strict-atime, lazytime, submount, snap-stable, nosec, and born.

## Control flow
Generated mount table data is scanned by `interpret.c:print_mount`, which joins all matching flag names.

## State and persistence behavior
Static lookup data only.

## Dependencies and integration points
Tracks `include/uapi/linux/mount.h` and must stay synchronized with `print_mount` buffer sizing. Integrated with syscall argument interpretation and normalization of mount actions.

## Risks and test signals
Risks are table/print buffer mismatch and Linux mount API drift. Tests should cover common flags, combined recursive/bind output, zero/unknown fallback, and new mount syscalls.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/mounttab.h -->
