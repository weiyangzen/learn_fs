# sources/security-integrity/selinux/libsemanage/src/semanage_store.c

## Purpose
Implements local SELinux semanage module-store filesystem handling: path initialization, store creation, sandbox/final directory construction, commit promotion, lock management, module path discovery, policydb file I/O, external verifier execution, and file/netfilter context sorting.

## APIs, control flow, and state
`semanage_check_init()` lazily fills global path tables for active, previous, tmp, and final policy locations. `semanage_create_store()`, `semanage_make_sandbox()`, and `semanage_make_final()` prepare persistent and temporary trees. `semanage_install_sandbox()` validates/compiles contexts, calls `semanage_commit_sandbox()`, increments `commit_num`, syncs the sandbox, takes the active lock, renames active to previous, tmp to active, installs final files, optionally reloads policy, and may remove the previous store. File helpers copy via `*.tmp` plus rename, recurse directories, remove directories, and restore SELinux labels/ownership through `semanage_setfiles()`.

## Dependencies and integration
Depends on libselinux paths/restorecon/reload semantics, libsepol policydb/CIL loaders, `database_policydb`, compressed-file mapping, configured external programs (`load_policy`, `setfiles`, `sefcontext_compile`, module/link/kernel verifiers), and handle configuration. `semanage_get_active_modules()` integrates module metadata and selects highest-priority enabled modules.

## Risks and test signals
Global path initialization is explicitly not thread-safe. Cross-device rename fallback is non-atomic. Recursive removal has early-return leak risk on error paths. Context sorting discards comments/blank lines and uses heuristic specificity. Commit rollback can leave an inconsistent store if nested renames/copies fail. Tests in the broader suite cover store access, locking, and netfilter sorting through `test_semanage_store`, but this work item includes only consumers in handle/fcontext tests.
