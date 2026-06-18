## sources/security-integrity/libcap/libcap/include/uapi/linux/capability.h

Purpose: bundled Linux UAPI capability definitions used to keep libcap independent of system kernel headers and aligned with upstream capability numbering.

Important APIs/types/constants: capability version constants, `__user_cap_header_struct`, `__user_cap_data_struct`, VFS capability xattr revisions/sizes, `struct vfs_cap_data`, `struct vfs_ns_cap_data`, named `CAP_*` values through `CAP_CHECKPOINT_RESTORE`, `CAP_LAST_CAP`, `cap_valid`, `CAP_TO_INDEX`, and `CAP_TO_MASK`.

Control flow: header definitions only; kernel/user conditional defines default legacy version for userspace.

State/persistence: defines binary ABI layouts for capget/capset and file xattrs.

Dependencies/integration: included by public `sys/capability.h`, parsed by `libcap/Makefile` to generate `cap_names.list.h`, compared by `distcheck.sh`.

Risks: must track upstream Linux exactly for capability numbers and xattr structs; stale `CAP_LAST_CAP` causes missing names and tests to warn/fail.

Test signals: `distcheck.sh`, generated `cap_names.h`, `capsh --summary`, and compile/runtime tests against kernels with newer/older capability counts.
