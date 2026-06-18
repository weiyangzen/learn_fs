# sources/security-integrity/selinux/libsepol/include/sepol/policydb.h

Purpose: Declares the opaque public policydb and policy-file API.

Important APIs and types: Opaque `sepol_policy_file_t` and `sepol_policydb_t`; policy file create/free, memory/FILE setters, length getter, handle setter; policydb create/free, type/version/unknown/target setters, optimize, read/write, image conversion, MLS and compat-net queries.

Control flow: Callers allocate a policy file wrapper around memory or `FILE`, allocate a policydb, read or configure it, mutate/query it through other APIs, then write or convert it.

State and persistence: `sepol_policydb_t` owns an internal `policydb`. `sepol_policy_file_t` references caller memory/streams or computes output length.

Dependencies and integration points: Foundation for all public libsepol record, module, context, and service APIs.

Risks: Type/version compatibility is strict. Memory-backed policy files need correct length and lifetime. Unknown-class behavior and target platform affect kernel semantics.

Test signals: Read/write round trips for kernel/base/module policies, image conversion, version bounds, and invalid policy images are core tests.
