# sources/security-integrity/selinux/libsepol/fuzz/binpolicy-fuzzer.c

Purpose: Defines a libFuzzer harness for binary SELinux policy images and module/base policy processing.

Important APIs and functions: `LLVMFuzzerTestOneInput()` drives `policydb_init`, `policydb_read`, `policydb_load_isids`, `policydb_optimize`, external `policydb_validate`, `check_assertions`, `hierarchy_check_constraints`, `policydb_write`, kernel-to-conf/CIL conversion, `link_modules`, and `expand_module`. `write_binary_policy()` wraps `policydb_write` to a `FILE`.

Control flow: The input is exposed as a memory `policy_file`; parse failures exit quietly. Valid kernel policies are optimized/validated/written/converted. Base policies are linked, expanded into `out`, checked, written, and converted.

State and persistence: State is local `policydb_t`, output policydb, SID table, and `/dev/null` stream. Cleanup destroys policydbs and SID table on all exits.

Dependencies and integration points: Exercises libsepol binary reader, module linker/expander, assertion and hierarchy checks, and CIL/conf emitters.

Risks: Calls `abort()` on internal invariant failures, intentionally turning unexpected successful parse plus failed write/convert/validate into fuzzer findings. Null handle paths must tolerate diagnostics.

Test signals: Fuzzer crashes, sanitizer reports, timeouts, and corpus coverage over kernel/base/module policy branches are key signals.
