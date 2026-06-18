# sources/user-network-fs/samba/source3/lib/netapi/examples/join/getjoininformation.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/join/getjoininformation.c

Purpose: Demonstrates reading current machine join status with `NetGetJoinInformation()`.

Important APIs/types/functions: Uses `NetSetupUnknownStatus`, `NetSetupUnjoined`, `NetSetupWorkgroupName`, and `NetSetupDomainName` result types.

Control flow: Parses optional host, calls `NetGetJoinInformation()`, switches on the returned join type, prints human-readable status and name, frees the name buffer, and cleans up.

State and persistence behavior: Read-only machine/domain membership query.

Dependencies and integration points: Baseline status check for join/unjoin/offline join examples and GUI initialization.

Risks: Unknown types are printed but not interpreted. Name buffer ownership must be released with `NetApiBufferFree()`.

Test signals: Run on unjoined, workgroup, and domain-joined systems and compare status labels.
