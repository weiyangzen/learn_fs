# sources/security-integrity/selinux/secilc/secilcheck.c

Purpose: `secilcheck` verifies CIL neverallow rules against an existing binary policy. It converts declarations from the binary policy into CIL, adds user-provided neverallow CIL files, compiles the CIL DB, and invokes libcil neverallow checking against the original policydb.

Important APIs and flow: `get_binary_policy_db` opens, stats, mmaps, and reads a binary policy through `sepol_policydb_read`. `add_decls_to_cil` uses `open_memstream` and `sepol_kernel_policydb_decls_to_cil` to feed binary declarations into `cil_add_file`. `add_cil_file` reads neverallow files, skipping empty files. `main` accepts `-Q`, `-m`, `-v`, and `-h`, requires at least two positional inputs, then runs `cil_compile` and `cil_check_neverallows_against_pdb`.

State and persistence: it writes no output files; state is memory-mapped policy input, a transient `sepol_policydb_t`, and a transient `cil_db`. Risks: `fd` is not initialized before error cleanup in `get_binary_policy_db`, `sb.st_size` is used in cleanup even if `fstat` fails, `mmap` asks for `PROT_WRITE` despite `MAP_PRIVATE` read-only use, and `map` cleanup checks `if (map)` rather than excluding `MAP_FAILED`. Test signals should include invalid files, zero-length policy, declaration conversion failures, valid no-violation cases, and violation exit status.
