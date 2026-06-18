# sources/security-integrity/selinux/libsepol/include/sepol/ports.h

Purpose: Declares public collection operations for port contexts in a policydb.

Important APIs and functions: `sepol_port_count`, `exists`, `query`, `modify`, and `iterate`.

Control flow: Functions search/update `OCON_PORT` entries using keys from `port_record.h`, returning public record copies.

State and persistence: `modify` changes in-memory policydb state; persistence requires writing the policydb.

Dependencies and integration points: Depends on policydb, handle, and port record APIs; used by semanage-like tools.

Risks: Port-range overlaps and protocol-specific ordering can affect lookups. Iterator callback ownership follows the temporary-record pattern.

Test signals: Multiple protocols, overlapping/missing ranges, modification, count, and iterator stop/error paths provide coverage.
