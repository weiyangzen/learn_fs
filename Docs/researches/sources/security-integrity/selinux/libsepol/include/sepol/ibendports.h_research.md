# sources/security-integrity/selinux/libsepol/include/sepol/ibendports.h

Purpose: Declares collection operations for InfiniBand end port entries in a policydb.

Important APIs and functions: `sepol_ibendport_count`, `exists`, `query`, `modify`, and `iterate`.

Control flow: Callers create keys/records with `ibendport_record.h`, then query or upsert entries in the policydb object-context list.

State and persistence: `modify` mutates policydb ocontext state; query/iterate materialize public record copies.

Dependencies and integration points: Integrates public policydb, handle, and IB end port record APIs. Internally corresponds to SELinux `ibendportcon`.

Risks: Range and identity uniqueness must match kernel policy semantics. Iterator callback ownership mirrors other record APIs: temporary records should be cloned if retained.

Test signals: Count/query/modify/iterate against policies with `ibendportcon` entries validate behavior.
