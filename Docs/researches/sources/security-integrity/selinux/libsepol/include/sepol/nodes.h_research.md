# sources/security-integrity/selinux/libsepol/include/sepol/nodes.h

Purpose: Declares collection APIs for network node contexts in a policydb.

Important APIs and functions: `sepol_node_count`, `exists`, `query`, `modify`, and `iterate`.

Control flow: Callers create node keys/records, then functions search or update the policydb object-context lists for IPv4/IPv6 nodes.

State and persistence: `modify` changes in-memory policydb state; write APIs persist it.

Dependencies and integration points: Depends on policydb, handle, and node record APIs. Integrates external tools with `nodecon` entries.

Risks: Overlapping CIDR-like ranges and family-specific ordering can affect lookup semantics. Iterator callbacks must respect temporary record ownership.

Test signals: Multiple node entries, family mismatch, missing keys, and iteration behavior validate the collection layer.
