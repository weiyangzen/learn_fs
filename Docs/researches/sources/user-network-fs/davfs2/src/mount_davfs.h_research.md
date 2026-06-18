# sources/user-network-fs/davfs2/src/mount_davfs.h

## Purpose
`mount_davfs.h` defines the central `dav_args` configuration structure and public declarations for the davfs2 mount helper. It documents the mount/daemon lifecycle and provides the cross-module contract that `mount_davfs.c`, `webdav.c`, cache, and kernel-interface initialization consume.

## Important APIs, Types, and Functions
- `typedef struct dav_args`: collects almost all parsed configuration, security, network, cache, and debug settings. Comments annotate the expected source of each field and therefore the precedence model.
- `main(int argc, char *argv[])`: declared with a long lifecycle comment describing setuid startup, validation, daemonization, running, and cleanup.
- `dav_user_input_hidden(const char *prompt)`: hidden-input prompt used by mount and WebDAV TLS client certificate handling.

## Control Flow
The header’s lifecycle comment is an architectural map: gather and validate input, initialize kernel/WebDAV/cache modules, fork into parent mount bookkeeping plus daemon loop, then terminate through signal or unmount-driven loop exit and close modules. `dav_args` fields are populated in phases by command line, fstab, system config, user config, secrets, environment, and interactive prompts.

## State and Persistence
`dav_args` carries persistent/runtime decisions: mount options, uid/gid/modes, WebDAV endpoint, certificate and secrets paths, credentials, proxy settings, lock/cookie/redirect behavior, retry and timeout policy, character sets, custom headers, cache directories and sizing, refresh/upload behavior, memory tuning, and debug flags. The struct owns many heap strings that `delete_args()` in `mount_davfs.c` frees and partially zeroes.

## Dependencies and Integration Points
It depends on standard POSIX types (`uid_t`, `gid_t`, `mode_t`, `time_t`, `size_t`) via including translation units. `webdav.h` relies on this type for `dav_init_webdav(const dav_args *)`; cache and kernel modules also take it as initialization input. Defaults are supplied from `defaults.h` and interpreted by the mount helper.

## Risks and Edge Cases
The struct is a broad mutable bag, so initialization completeness is critical. Adding fields requires updates to `new_args()`, `delete_args()`, config parsing, debug logging, and consumers. The comments encode precedence but the type itself cannot enforce it. Credential fields must remain carefully zeroed on free, and ownership transfer for `cl_username` to `username` in `parse_secrets()` is a notable convention.

## Test Signals
Tests should assert that `new_args()` initializes every field consistently with documented defaults, `delete_args()` handles partially initialized structs, and every config/secrets field has a corresponding parser and cleanup path. Integration tests should confirm that WebDAV/cache/kernel modules receive expected values after layered config precedence.
