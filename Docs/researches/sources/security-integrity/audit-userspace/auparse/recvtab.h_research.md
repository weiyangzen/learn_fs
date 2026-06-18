<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/recvtab.h -->
# sources/security-integrity/audit-userspace/auparse/recvtab.h

## Purpose
Maps socket send/receive message flag bits to names.

## Important APIs, types, and functions
The `_S` table includes `MSG_OOB`, `MSG_PEEK`, routing/truncation/wait flags, connection flags, error queue, nosignal/more, batch, fastopen, cmsg cloexec, and compat bits.

## Control flow
Generated data is scanned by `interpret.c:print_recv` for send/receive syscall arguments.

## State and persistence behavior
Static table data only.

## Dependencies and integration points
Tracks Linux socket headers. Used by `print_a2`/`print_a3` for recv/send variants.

## Risks and test signals
Risks are flag drift and signed/high-bit parsing. Tests should cover low and high bit flags, combined output, and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/recvtab.h -->
