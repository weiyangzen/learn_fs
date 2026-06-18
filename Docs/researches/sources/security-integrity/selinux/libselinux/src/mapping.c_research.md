<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/mapping.c -->
# sources/security-integrity/selinux/libselinux/src/mapping.c

## Purpose
Maintains userspace-to-kernel security class and permission mappings so object managers can use stable local class indices while querying the loaded SELinux policy.

## Important APIs, Types, And Functions
`struct selinux_mapping` stores a kernel class value and permission bit translations. `selinux_set_mapping()` builds the current mapping from `struct security_class_mapping`. `map_class()`, `unmap_class()`, `map_perm()`, `unmap_perm()`, and `map_decision()` translate classes, permission masks, and `struct av_decision`.

## Control Flow
Setting a mapping resets AVC state, resolves every class and permission string through policy stringrep helpers, handles unknown entries according to `security_reject_unknown()` and `security_deny_unknown()`, then publishes the mapping size last so setup lookups stay raw.

## State And Persistence Behavior
State is process-global heap memory in `current_mapping`; it is replaced on every successful setup and freed on errors. No disk state is written.

## Dependencies And Integration Points
Integrates with `avc_reset()`, `string_to_security_class()`, `string_to_av_perm()`, `security_reject_unknown()`, `security_deny_unknown()`, logging callbacks, and AVC decisions.

## Risks And Test Signals
Risks include global non-locked replacement, unknown-class handling, permission bit width assumptions, and `map_perm()` returning `EINVAL` when no known bit maps. Tests should exercise reject/allow unknown policy modes, empty permission names, unmapped fallback behavior, and `av_decision` remapping fields.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/mapping.c -->
