<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/nfprototab.h -->
# sources/security-integrity/audit-userspace/auparse/nfprototab.h

## Purpose
Names netfilter protocol-family ids for packet audit records.

## Important APIs, types, and functions
The `_S` table maps families such as unspecified, inet, ipv4, arp, netdev, bridge, ipv6, and decnet.

## Control flow
Generated `nfproto_i2s` is used by `interpret.c:print_nfproto`, which parses decimal field values.

## State and persistence behavior
Static table only.

## Dependencies and integration points
Tracks Linux netfilter headers and feeds `AUPARSE_TYPE_NFPROTO`. It also affects hook-table selection in contextual hook interpretation.

## Risks and test signals
Risks are missing protocol families and mismatched family/hook semantics. Tests should include ARP versus inet families and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/nfprototab.h -->
