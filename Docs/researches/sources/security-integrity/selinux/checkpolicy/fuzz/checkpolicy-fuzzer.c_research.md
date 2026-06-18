# sources/security-integrity/selinux/checkpolicy/fuzz/checkpolicy-fuzzer.c

Purpose: libFuzzer target for SELinux checkpolicy parsing, linking, expansion, validation, and output conversion.

Important APIs/functions: `full_write()` writes fuzz data robustly. `read_source_policy()` feeds data through a memfd and the two-pass parser, handling parser longjmp state and cleanup. `LLVMFuzzerTestOneInput()` interprets first bytes as target platform, MLS flag, and policy version, then parses, links, expands, validates, optimizes/sorts, and writes binary/conf/CIL to `/dev/null`.

Control flow: rejects inputs shorter than three bytes or invalid selector bytes. For valid source bodies, it initializes policydbs, parses, expands base policies to kernel policies when needed, loads initial SIDs, validates final policydb, aborts if invalid policy can be emitted, and resets global parser/module state.

State and dependencies: uses parser globals, `id_queue`, `policydbp`, `mlspol`, `policydb_errors`, memfd, libsepol, and module compiler reset.

Risks and test signals: global parser state cleanup is critical for repeated fuzz iterations. CIFuzz and OSS-Fuzz exercise this target under sanitizers.
