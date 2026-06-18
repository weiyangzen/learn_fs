<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/icmptypetab.h -->
# sources/security-integrity/audit-userspace/auparse/icmptypetab.h

## Purpose
Maps ICMP type numbers to human-readable audit strings for netfilter packet records.

## Important APIs, types, and functions
The `_S` table includes echo, unreachable, redirect, time-exceeded, parameter-problem, timestamp, information, and address-mask ICMP types.

## Control flow
Generated `icmptype_i2s` is called by `interpret.c:print_icmptype`, which parses decimal values.

## State and persistence behavior
Static compile-time data only.

## Dependencies and integration points
Based on `include/uapi/linux/icmp.h`; integrated with field type `AUPARSE_TYPE_ICMPTYPE`.

## Risks and test signals
Risk is partial ICMP coverage, especially uncommon or newer types. Tests should verify common type output and `unknown-icmp-type` fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/icmptypetab.h -->
