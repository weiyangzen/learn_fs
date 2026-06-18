<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/ioctlreqtab.h -->
# sources/security-integrity/audit-userspace/auparse/ioctlreqtab.h

## Purpose
Provides a curated mapping of ioctl request numbers to names for audit syscall interpretation.

## Important APIs, types, and functions
The `_S` table covers selected keyboard/display, CD-ROM, terminal, socket/interface, pseudo-terminal, and DRM ioctls. It is explicitly not comprehensive.

## Control flow
Generated `ioctlreq_i2s` feeds `interpret.c:print_ioctl_req`; unknown requests are rendered as hex.

## State and persistence behavior
Static table data only.

## Dependencies and integration points
Values reference Linux kd, cdrom, asm-generic ioctl, and DRM headers. Used when `print_a1` sees `ioctl`.

## Risks and test signals
Risk is sparse coverage and arch-specific ioctl encoding. Tests should assert known request names and hex fallback for unknown requests.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/ioctlreqtab.h -->
