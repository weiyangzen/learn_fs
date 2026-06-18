# sources/security-integrity/selinux/libsepol/include/sepol/kernel_to_cil.h

Purpose: Declares conversion APIs from an in-memory kernel policydb to CIL text.

Important APIs and functions: `sepol_kernel_policydb_to_cil(FILE *out, struct policydb *pdb)` and `sepol_kernel_policydb_decls_to_cil(FILE *out, struct policydb *pdb)`.

Control flow: Callers provide a populated kernel `policydb` and output stream; implementation walks policy symbols/rules and emits CIL.

State and persistence: No state is declared. Output is persisted only through the supplied `FILE`.

Dependencies and integration points: Includes `policydb/policydb.h`; used by tools and the binary policy fuzzer to exercise text emission.

Risks: Header lacks include guards and uses `FILE` while including `<stdlib.h>` rather than `<stdio.h>`, relying on prior includes in many build contexts.

Test signals: Conversion of valid kernel policies, round-trip comparison with expected CIL, and fuzzer execution validate this contract.
