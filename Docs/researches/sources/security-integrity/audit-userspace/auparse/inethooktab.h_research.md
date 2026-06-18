<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/inethooktab.h -->
# sources/security-integrity/audit-userspace/auparse/inethooktab.h

## Purpose
Names IPv4/IPv6 netfilter hook numbers for audit packet records.

## Important APIs, types, and functions
The `_S` table maps `0..5` to `PREROUTING`, `INPUT`, `FORWARD`, `OUTPUT`, `POSTROUTING`, and `BROUTING`.

## Control flow
Generated `inethook_i2s` is selected by `interpret.c:print_hook` unless the current record family is ARP, in which case ARP hook lookup is used.

## State and persistence behavior
Static table data only.

## Dependencies and integration points
Integrates with `NFPROTO_*` family parsing and netfilter audit fields `hook` and `family`.

## Risks and test signals
Risks are wrong family selection and missing hook constants. Tests should preserve cursor position after `print_hook`, check inet and ARP family paths, and verify unknown hook fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/inethooktab.h -->
