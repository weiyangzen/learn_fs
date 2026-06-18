# sources/security-integrity/selinux/libsepol/include/sepol/module_to_cil.h

Purpose: Declares conversion APIs from module policydb/package formats to CIL.

Important APIs and functions: `sepol_module_policydb_to_cil(FILE *fp, struct policydb *pdb, int linked)`, `sepol_module_package_to_cil`, and `sepol_ppfile_to_module_package`.

Control flow: Conversion accepts either a module policydb or package and writes CIL to a stream; pp-file parsing creates a module package before conversion.

State and persistence: No global state; package parsing allocates a `sepol_module_package` returned to the caller.

Dependencies and integration points: Includes `sepol/module.h` and internal `policydb.h`; used by semodule/decompiler-style tooling.

Risks: Header has no include guard and relies on `FILE` via transitive includes. The `linked` flag changes emitted semantics and must match caller state.

Test signals: Module package to CIL round trips and linked/unlinked output comparisons validate behavior.
