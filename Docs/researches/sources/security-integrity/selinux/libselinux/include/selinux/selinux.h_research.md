# sources/security-integrity/selinux/libselinux/include/selinux/selinux.h

## Purpose
`selinux.h` is the central public libselinux header. It declares status queries, context get/set wrappers, xattr helpers, socket peer context access, policy decision APIs, boolean management, class/permission mapping, file-context matching compatibility APIs, SELinux path discovery, access checking, translation, login mapping, and configuration reset functions.

## Important APIs, types, and functions
Major types include deprecated `security_context_t`, `access_vector_t`, `security_class_t`, `struct av_decision`, `struct selinux_opt`, `union selinux_callback`, `SELboolean`, and `struct security_class_mapping`. Important functions include `is_selinux_enabled()`, `getcon()`/`setcon()` families, exec/fs/key/socket create context APIs, file xattr context APIs, `security_compute_*()`, `security_load_policy()`, `selinux_mkload_policy()`, `selinux_init_load_policy()`, boolean APIs, context validation/canonicalization, enforcing and unknown-permission queries, class/permission string mapping, `matchpathcon*()` compatibility APIs, policy path getters, `selinux_check_access()`, `set_selinuxmnt()`, `selinuxfs_exists()`, translation/color APIs, `getseuser*()`, file-context verification/defaulting, and `selinux_reset_config()`.

## Control flow
Callers use status/path APIs to discover SELinux availability and policy layout, context APIs to read or set process/file/socket labels, policy APIs to compute or load decisions, boolean APIs to stage and commit changes, and access-check APIs to audit permission decisions. Callback APIs allow logging, audit formatting, context validation, and policy event handling to be customized globally.

## State and persistence behavior
Many functions operate on kernel SELinux state through `/proc`, xattrs, selinuxfs, policy files, booleans, and process attributes. Some set process-local state for future exec/file/key/socket creation. Callback registration and cached configuration are process-global. Persistent effects include file label changes, boolean commits, policy loading, and config/path-root changes.

## Dependencies and integration points
The header depends on Linux system types and `<asm/bitsperlong.h>`. It is consumed by almost every libselinux user, including AVC, labeling, restorecon, login/session setup, package managers, init systems, and object managers.

## Risks and edge cases
The API mixes raw and translated context variants; callers must choose correctly. Many returned strings require `freecon()`, `freeconary()`, or `free()` depending on function. Deprecated APIs remain for compatibility and may always fail or be unsupported, such as runtime disable on newer kernels and local boolean loading. `selinux_reset_config()` is explicitly not thread-safe. Process context changes can invalidate access to already-open descriptors unless policy permits use.

## Test signals
Coverage should include enabled/disabled kernels, raw versus translated context round trips, file/xattr operations on symlinks and fds, process attribute get/set, compute decision APIs, boolean staging/commit, class/permission mapping, matchpathcon compatibility, path getters under alternate roots, access checks with callbacks, policy load failures, and thread-safety boundaries around global reset/configuration.
