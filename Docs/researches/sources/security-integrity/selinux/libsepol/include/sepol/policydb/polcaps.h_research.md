# sources/security-integrity/selinux/libsepol/include/sepol/policydb/polcaps.h

Purpose: Defines known SELinux policy capability IDs and lookup helpers.

Important APIs and symbols: Capability enum entries from `POLICYDB_CAP_NETPEER` through `POLICYDB_CAP_BPF_TOKEN_PERMS`, `POLICYDB_CAP_MAX`, `sepol_polcap_getnum`, and `sepol_polcap_getname`.

Control flow: Parser/converter code maps textual policycap names to numbers and back for ebitmap storage/emission.

State and persistence: Capability bits are stored in `policydb_t.policycaps`.

Dependencies and integration points: Used by policydb parsing/writing, kernel-to-text conversion, and service behavior checks.

Risks: Enum ordering is persistent policy ABI. Adding capabilities requires updates to name maps and policy version support.

Test signals: Name/number round trips, unknown-name handling, and binary policies containing each cap validate behavior.
