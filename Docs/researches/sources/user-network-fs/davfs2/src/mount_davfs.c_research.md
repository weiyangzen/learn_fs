# sources/user-network-fs/davfs2/src/mount_davfs.c

## Purpose
`mount_davfs.c` is the setuid mount helper and daemon launcher for davfs2. It gathers command-line, fstab, configuration, environment, and secrets data into `dav_args`, validates mount permissions and filesystem support directories, initializes WebDAV/cache/kernel modules, forks into daemon mode, writes mount bookkeeping, and drives the FUSE/kernel message loop until unmount or termination.

## Important APIs, Types, and Functions
- `main(int argc, char **argv)`: top-level mount lifecycle. It parses options, drops/reacquires effective root as needed, checks fstab for non-root users, reads config/secrets, prevents duplicate mounts, switches persona, initializes `webdav`, `cache`, and `kernel_interface`, forks, writes mtab/utab in the parent, and runs `dav_fuse_loop()` in the child.
- `dav_user_input_hidden()`: public hidden-input helper used for passwords and client certificate decryption.
- `change_persona()`: permanently changes process group to configured `dav_group` and sets effective uid to `dav_user` or invoking user before daemon final privilege drop.
- `check_dirs()`: validates `/proc/mounts` or mtab/utab usage, creates runtime/cache/config/cert directories, checks ownership/mode constraints, and copies default per-user config/secrets templates.
- `check_fstab()`: for non-root mounts, canonicalizes fstab mountpoints, verifies URL/type/options match the invocation, and requires `user` or `users`.
- `check_permissions()`: enforces that non-root users cannot mount with a foreign uid, must belong to requested gid, and must be in the configured davfs group.
- `parse_commandline()`, `get_options()`, `parse_config()`, `parse_secrets()`: implement precedence across `-o`, config files, secrets files, environment password, and interactive prompts.
- `split_uri()`: davfs-specific URI parser for http/https URLs, default path, host normalization, IPv6 brackets, and no userinfo.
- `write_mtab_entry()` and `save_pid()`: persist runtime bookkeeping.

## Control Flow
The mount starts in the user’s locale, syslogs startup, parses `-o` options plus URL/mountpoint, then verifies it is installed setuid root. It temporarily drops effective root to the invoking uid while reading user-specific policy. Non-root callers must match an fstab entry. Config is read system-first, then user or explicitly supplied config. Directory and permission checks run before secrets so missing private files can be created. Secrets are read system-first as root, then user, then `DAVFS_PASSWORD` and interactive prompts can override.

After duplicate mount and pidfile checks, `change_persona()` sets the group/persona for the future daemon. `dav_init_webdav()`, `dav_init_cache()`, and `dav_init_kernel_interface()` are initialized before fork. Parent writes `/etc/mtab` or util-linux `utab` metadata and exits. Child installs SIGTERM/SIGHUP handlers, permanently drops root with `setuid(daemon_id)`, detaches from terminal with `setsid()` and `/dev/null`, writes a pid file, and enters `dav_fuse_loop(dev, mpoint, buf_size, idle_time, is_mounted, &keep_on_running, debug)`. Shutdown closes cache and WebDAV, removes the pid file, and returns.

## State and Persistence
Global state includes `url`, canonical `mpoint`, Linux `mounts`, `pidfile`, `keep_on_running`, and `got_sigterm`. Persistent state touched by the helper includes per-user `~/.davfs2` config/cache/cert/secrets templates, system runtime directory `DAV_SYS_RUN`, pid files named from mountpoint slashes converted to dashes, optional system cache, `/etc/mtab` or `/var/run/mount/utab`, and davfs cache state through `dav_init_cache()`/`dav_close_cache()`. Secrets are zeroed before free in `delete_args()` and `read_secrets()` zeroes parsed input lines.

## Dependencies and Integration Points
This file integrates with `defaults.h` constants, `util.h` error/canonicalization helpers, Neon utility functions (`ne_concat`, `ne_strdup`, URI defaults), davfs modules `kernel_interface.h`, `cache.h`, and `webdav.h`, system passwd/group databases, fstab/mtab APIs, Linux/FreeBSD mount tables, syslog, termios, and setuid/setgid process APIs. The `dav_args` structure defined in `mount_davfs.h` is the cross-module configuration contract consumed by WebDAV, cache, and kernel layers.

## Risks and Edge Cases
This is security-sensitive setuid code. Ownership/mode checks are extensive but failures in privilege switching or path canonicalization are fatal. `parse_commandline()` reports canonicalization failure using `mpoint` after a NULL return rather than the original path, which can weaken diagnostics. `arg_to_int()` does not require full-string consumption after `strtol`, so values with numeric prefixes may be accepted. `write_mtab_entry()` checks `if (!ld)` after `open()`, so a valid fd 0 would be treated as failure; unlikely after normal stdio state, but still a correctness risk. Shell-free parsing is used for config/secrets, but `umount_davfs.c` uses shell commands separately. Debug logging can expose secrets when `DAV_DBG_SECRETS` is enabled, intentionally but dangerously. Fork-before-mount success means parent/child coordination depends on signals and may leave stale pid/mtab state on rare failures as the header notes.

## Test Signals
Useful tests include URI parsing with schemes, IPv6, missing path, userinfo rejection, and trailing slash behavior; config parser quoting/escaping and mountpoint sections; fstab option equivalence for non-root mounts; secrets precedence and permission failures; no-proxy matching; pidfile naming; duplicate mount detection against mocked mount tables; and daemon lifecycle tests verifying pid file cleanup and signal-triggered graceful shutdown. Security tests should cover wrong owner/mode for secrets/client certs and non-root membership failures.
