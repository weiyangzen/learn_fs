# sources/security-integrity/selinux/libsepol/include/sepol/ibpkeys.h

Purpose: Declares policydb collection operations for InfiniBand pkey contexts.

Important APIs and functions: `sepol_ibpkey_count`, `exists`, `query`, `modify`, and `iterate`.

Control flow: Keys identify subnet-prefix/pkey ranges; collection functions search or mutate the policydb object-context structures and return public records.

State and persistence: `modify` persists changes in the in-memory policydb until the caller writes it. Other operations are read-only.

Dependencies and integration points: Depends on `policydb.h`, `handle.h`, and `ibpkey_record.h`; integrates with SELinux `ibpkeycon` policy handling.

Risks: Overlapping pkey ranges and prefix normalization are subtle policy correctness cases. Callback-return conventions must be honored.

Test signals: Policies with multiple pkey ranges, overlapping/missing queries, and iteration early exit/error paths provide coverage.
