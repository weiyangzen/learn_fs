# sources/security-integrity/selinux/libsemanage/src/genhomedircon.h

Purpose: declares the internal homedir file-context generation entry point used by libsemanage commit/build logic.

Important API: `semanage_genhomedircon(semanage_handle_t *sh, sepol_policydb_t *policydb, int usepasswd, char *ignoredirs)`. The include of `utilities.h` supplies shared utility/list declarations and indirectly the semanage handle context used by the implementation.

Control flow/integration: callers pass the active semanage handle, loaded policydb, whether passwd scanning should be used, and a semicolon-separated ignored directory list from configuration. The implementation writes generated contexts into the temporary store.

State/persistence: no state in the header. The implementation reads account/config files and writes `file_contexts.homedirs`. Risks are ABI mismatch with the implementation and passing a mutable `ignoredirs` string because the implementation tokenizes it with `strtok_r`. Test signals are compile coverage and commit paths that generate homedir contexts with and without passwd scanning.
