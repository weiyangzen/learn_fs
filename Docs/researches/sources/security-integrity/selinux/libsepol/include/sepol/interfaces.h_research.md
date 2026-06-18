# sources/security-integrity/selinux/libsepol/include/sepol/interfaces.h

Purpose: Declares public collection operations for network interface policy entries.

Important APIs and functions: `sepol_iface_count`, `exists`, `query`, `modify`, and `iterate`.

Control flow: Functions search or mutate the policydb `OCON_NETIF` list using keys from `iface_record.h`.

State and persistence: `modify` updates in-memory policydb state; write APIs are needed for persistence to binary policy.

Dependencies and integration points: Depends on public policydb, interface record, and handle APIs; connects external tools to SELinux `netifcon` data.

Risks: Interface names are environment-specific but policydb entries are static. Iterator callback ownership and error propagation mirror the other collection APIs.

Test signals: Query/modify of policies with interface and packet contexts, iteration early stop, and missing-key behavior are important.
