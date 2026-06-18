# sources/security-integrity/selinux/libsemanage/src/semanage_store.h

## Purpose
Declares the internal module-store contract used by libsemanage direct connections.

## APIs, types, and state
Defines `enum semanage_store_defs` for active/previous/tmp stores, `enum semanage_sandbox_defs` for store-relative artifacts, and final-path enums for installed SELinux policy outputs. Exposes path accessors, store creation/access checks, sandbox/final creation, lock acquisition/release, commit serial lookup, CIL/policydb loading/writing, verifier hooks, context sorting, file copy, and `semanage_setfiles()` configuration.

## Dependencies and integration
Includes `handle.h`, sepol module/CIL types, and public bool/time headers. It is the bridge between handle/direct transaction logic and concrete filesystem paths.

## Risks and test signals
The enum ordering is a persistence ABI for `semanage_store.c` path arrays; adding entries requires synchronized updates to relative-path tables. Callers rely on `semanage_check_init()` before accessing returned const paths.
