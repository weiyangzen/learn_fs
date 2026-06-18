# sources/security-integrity/selinux/libsepol/include/sepol/kernel_to_conf.h

Purpose: Declares conversion from an in-memory kernel policydb to policy.conf text.

Important APIs and functions: `sepol_kernel_policydb_to_conf(FILE *fp, struct policydb *pdb)`.

Control flow: Caller supplies an output stream and kernel policydb; implementation emits checkpolicy-style configuration text.

State and persistence: No state is owned. Generated text persists in the caller-provided stream.

Dependencies and integration points: Includes internal policydb definitions and is used by tools/fuzzers to check decompilation paths.

Risks: Like `kernel_to_cil.h`, it lacks an include guard and relies on `FILE` availability from included headers or transitive includes.

Test signals: Conversion success for representative kernel policies and comparison against parseable/conf-equivalent output are primary tests.
