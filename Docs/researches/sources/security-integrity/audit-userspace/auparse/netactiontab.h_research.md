<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/netactiontab.h -->
# sources/security-integrity/audit-userspace/auparse/netactiontab.h

## Purpose
Maps netfilter audit target action ids to action names.

## Important APIs, types, and functions
The `_S` entries map `0`, `1`, and `2` to `ACCEPT`, `DROP`, and `REJECT`.

## Control flow
Generated `netaction_i2s` is used by `interpret.c:print_netaction` for `AUPARSE_TYPE_NETACTION`.

## State and persistence behavior
Static lookup data only.

## Dependencies and integration points
Based on `xt_AUDIT.h`, integrated with netfilter packet/config audit records.

## Risks and test signals
Risks are new actions not represented and decimal/hex interpretation mistakes. Tests should cover all known values and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/netactiontab.h -->
