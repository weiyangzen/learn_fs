# sources/security-integrity/selinux/checkpolicy/fuzz/min_pol.conf

Purpose: minimal non-MLS SELinux policy seed for checkpolicy fuzzing.

Important content: declares core classes and SIDs, process permissions, default roles for file-like classes, a type with aliases, an allow rule, role/user mappings, SID contexts, and `fs_use_trans` entries.

Control flow/integration: no executable flow. Used as a seed corpus or baseline policy shape for the fuzzer/parser path.

State and dependencies: policy text depends on checkpolicy language grammar and libsepol semantic validation.

Risks and test signals: intentionally small but semantically complete enough to parse and expand. It provides non-MLS coverage for class, SID, typealias, allow, role, user, and filesystem labeling constructs.
