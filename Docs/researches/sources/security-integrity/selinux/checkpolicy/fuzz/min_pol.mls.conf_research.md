# sources/security-integrity/selinux/checkpolicy/fuzz/min_pol.mls.conf

Purpose: minimal MLS-enabled SELinux policy seed for checkpolicy fuzzing.

Important content: extends the non-MLS minimal policy with `sensitivity`, `dominance`, `category`, `level`, `mlsconstrain`, MLS-aware user range, and MLS-labeled SID and filesystem contexts.

Control flow/integration: policy text seed for parser/fuzzer runs where MLS flag is enabled. It exercises MLS grammar and semantic checks that are absent from `min_pol.conf`.

State and dependencies: depends on checkpolicy MLS grammar, level/category consistency, and libsepol validation.

Risks and test signals: catches regressions in MLS parsing, constraint handling, and context serialization. It is compact enough to mutate efficiently in fuzzing.
