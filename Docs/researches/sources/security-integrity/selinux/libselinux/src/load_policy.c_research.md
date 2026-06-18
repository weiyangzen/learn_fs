<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/load_policy.c -->
# sources/security-integrity/selinux/libselinux/src/load_policy.c

## Purpose
Loads a binary SELinux policy into the kernel and performs early-init policy setup. It bridges policy files under the configured policy root, `selinuxfs` control files, `/proc/cmdline`, and optional libsepol downgrade support.

## Important APIs, Types, And Functions
`security_load_policy()` writes policy bytes to `<selinux_mnt>/load`. `selinux_mkload_policy()` locates `policy.N`, optionally uses libsepol symbols to downgrade a newer policy to the running kernel policy version, mmaps the file, and calls `security_load_policy()`. `selinux_init_load_policy()` rereads config, mounts `/proc`, `/sys`, and `selinuxfs`, resolves enforcing mode, optionally disables SELinux, sets enforcing state, and invokes the load path.

## Control Flow
Policy selection starts at the max of kernel and libsepol-supported versions, walks down to the minimum supported version, maps the file, and retries older files if downgrade fails. Init loading gives kernel command-line `enforcing=` precedence over `/etc/selinux/config`, then config, then permissive fallback.

## State And Persistence Behavior
Persistent state is in kernel `selinuxfs`: `load` receives the policy image and `enforce` may be changed before policy load. The code temporarily mounts filesystems and may unmount `/proc` or `selinuxfs` after runtime-disable handling.

## Dependencies And Integration Points
Uses `policy.h`, config accessors, `security_policyvers()`, `security_getenforce()`, `security_setenforce()`, `security_disable()`, `set_selinuxmnt()`, and libsepol either linked directly or `dlopen()`ed in shared builds.

## Risks And Test Signals
Key risks are partial `write()` handling, downgrade retry correctness, mount side effects during init, and enforcing-mode precedence. Tests should cover missing selinuxfs, disabled kernel SELinux, multiple policy versions, failed downgrade fallback, and command-line/config combinations.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/load_policy.c -->
