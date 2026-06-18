# sources/security-integrity/selinux/libsepol/fuzz/secilc-fuzzer.c

Purpose: Defines a libFuzzer harness for secilc/CIL source parsing, compilation, policydb generation, optimization, and binary writing.

Important APIs and functions: `LLVMFuzzerTestOneInput()` configures a `cil_db`, calls `cil_add_file`, `cil_compile`, `cil_build_policydb`, `sepol_policydb_optimize`, `sepol_policy_file_create`, `sepol_policy_file_set_fp`, and `sepol_policydb_write`. `log_handler()` suppresses CIL log output.

Control flow: Fuzzer bytes are treated as an in-memory file named `"fuzz"`. Any parser/compiler/optimizer/write failure exits normally; only memory-safety bugs or unexpected crashes are findings.

State and persistence: Transient CIL db and `sepol_policydb_t` are freed at exit. Binary output goes to `/dev/null`; no corpus-derived files persist.

Dependencies and integration points: Integrates CIL public API, policydb public API, and the writer path.

Risks: It uses maximum policy version and default SELinux target, so alternative targets/options need separate fuzzing if desired. Silent normal exits require coverage tooling to prove deep paths are reached.

Test signals: libFuzzer coverage, sanitizer findings, and stable cleanup under malformed CIL are the primary validation signals.
