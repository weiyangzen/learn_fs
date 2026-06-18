# sources/security-integrity/selinux/libsepol/src/policydb_public.c

## Purpose
Implements the public libsepol wrapper API for policy files and policydb objects. It hides internal `policy_file_t`/`policydb_t` layout behind `sepol_policy_file_t` and `sepol_policydb_t` handles.

## Important APIs, Types, and Functions
Policy-file APIs: `sepol_policy_file_create`, `sepol_policy_file_set_mem`, `sepol_policy_file_set_fp`, `sepol_policy_file_get_len`, `sepol_policy_file_set_handle`, and `sepol_policy_file_free`. Policydb APIs: `sepol_policydb_create`, `sepol_policydb_free`, version bounds accessors, `sepol_policydb_set_typevers`, `sepol_policydb_set_vers`, `sepol_policydb_set_handle_unknown`, `sepol_policydb_set_target_platform`, `sepol_policydb_optimize`, `sepol_policydb_read`, `sepol_policydb_write`, `sepol_policydb_from_image`, `sepol_policydb_to_image`, `sepol_policydb_mls_enabled`, and `sepol_policydb_compat_net`.

## Control Flow
Creation allocates wrappers and initializes internal structures. File setters configure backing mode as memory, stdio, or length-counting mode when memory length is zero. Version/type setters validate requested values against kernel or module min/max ranges. Read/write/optimize/image functions delegate to internal policydb functions. `sepol_policydb_compat_net()` checks for absence of the `packet` class to enable older network-check compatibility mode.

## State and Persistence Behavior
Wrappers own their internal policydb and must be freed with `sepol_policydb_free()`. `sepol_policy_file_set_mem()` does not copy caller memory; it stores the pointer and length. `sepol_policy_file_get_len()` only succeeds after length-counting writes. Read/write persist through the configured policy file mode, and image conversion allocates caller-owned output buffers on success.

## Dependencies and Integration Points
Depends on `policydb_internal.h` for public structures and internal helpers, `debug.h`, policydb read/write/convert/optimize implementations, and hashtab lookup for compatibility mode. This is the stable C API layer used by external libsepol consumers.

## Risks and Edge Cases
`sepol_policy_file_set_mem(..., len=0)` switches to `PF_LEN`, which is a non-obvious overload: a zero-length memory input cannot be represented by this wrapper. The wrappers do little null checking beyond create/free. Callers must set policy type before `sepol_policydb_set_vers()` or version validation fails. `sepol_policydb_set_typevers()` sets max version as a side effect.

## Test Signals
API tests should cover create/free, memory and stdio read/write paths, length-counting writes and `get_len`, type/version validation, handle_unknown and target validation, optimize delegation, image round trip, MLS query, and `compat_net` behavior with and without a `packet` class.
