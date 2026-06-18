<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/fsconfig.h -->
# sources/security-integrity/audit-userspace/auparse/fsconfig.h

## Purpose
Maps `fsconfig(2)` command ids to names for new mount API audit records.

## Important APIs, types, and functions
The `_S` table covers `FSCONFIG_SET_FLAG`, string/binary/path/fd setting operations, and create/reconfigure/create-exclusive commands.

## Control flow
Generated `fsconfig_i2s` is called by `interpret.c:print_fsconfig`, which interprets `fsconfig` argument `a1`.

## State and persistence behavior
Static table data only.

## Dependencies and integration points
Tracks `include/uapi/linux/mount.h`. It integrates with `normalize_syscall_map.h`, where `fsconfig` is classified as a filesystem mount operation.

## Risks and test signals
Risk is new mount API command drift. Tests should include known command ids, unknown id fallback, and a normalized `fsconfig` syscall showing mount-related action/object classification.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/fsconfig.h -->
