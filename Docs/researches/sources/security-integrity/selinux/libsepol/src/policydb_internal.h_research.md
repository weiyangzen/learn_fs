# sources/security-integrity/selinux/libsepol/src/policydb_internal.h

## Purpose
Small private header that includes the public policydb API and exposes `policydb_target_strings[]` to internal source files needing target platform names.

## Important APIs, Types, and Functions
Declares `extern const char *const policydb_target_strings[];`, which is defined in `policydb.c` and indexed by target platform ids such as SELinux and Xen.

## Control Flow
No runtime control flow; only include guard `_SEPOL_POLICYDB_INTERNAL_H_`.

## State and Persistence Behavior
No owned state. It declares read-only global string storage owned by `policydb.c`.

## Dependencies and Integration Points
Includes `<sepol/policydb.h>` and is used by wrappers or helpers that need internal access to target platform display strings without depending directly on `policydb.c`.

## Risks and Edge Cases
The declaration exposes a global array without its size; callers must use valid target platform indexes and should rely on policydb bounds helpers where possible. Any change to target platform enum ordering must keep the definition in sync.

## Test Signals
Compilation and linker resolution are primary. Runtime tests that report target platform names through xperm or read errors indirectly cover this declaration.
