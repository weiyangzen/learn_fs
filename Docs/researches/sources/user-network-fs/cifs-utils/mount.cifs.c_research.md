<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/mount.cifs.c -->
# sources/user-network-fs/cifs-utils/mount.cifs.c

## Purpose

`mount.cifs.c` implements the setuid/capability-aware mount helper for CIFS and SMB3 filesystems. It validates user mounts, parses UNC paths and mount options, obtains credentials, resolves target addresses, invokes the kernel `mount(2)` call, retries selected failures, and updates mtab when appropriate.

## Important APIs, Types, and Functions

The central type is `struct parsed_mount_info`, which carries flags, host/share/prefix, options, domain, username, passwords, address list, and parsing state bits across the privilege-separated parent/child boundary. Major functions include `check_setuid`, `check_fstab`, `mount_usage`, `set_password`, `drop_capabilities`, `toggle_dac_capability`, `parse_cred_line`, `open_cred_file`, `get_password_from_file`, `parse_opt_token`, `parse_options`, `parse_unc`, `get_pw_from_env`, `uppercase_string`, `check_mtab`, `add_mtab`, `del_mtab`, `drop_child_privs`, optional `get_passwd_by_systemd`, `get_password`, `assemble_mountinfo`, `acquire_mountpoint`, and `main`.

## Control Flow

`main` validates setuid/root capability, drops to a restricted capability set, parses top-level mount options, canonicalizes the mountpoint, and forks. The child drops privileges, checks `/etc/fstab` for unprivileged users, reads environment and credential files, parses option strings, validates user mount flags, parses the UNC, resolves host addresses, defaults username, and prompts for a password when needed. The parent then iterates the comma-separated address list, assembles kernel options (`ip=`, `unc=`, parsed options, prefix path, passwords), calls `mount(orig_dev, ".", cifs_fstype, flags, options)`, retries connection errors against alternate addresses, retries uppercase share names for `ENXIO`, and can reassemble with `SUDO_UID` as `cruid` on Kerberos `ENOKEY`. It updates mtab unless `-n`, fake mount, or unusable mtab conditions apply.

## State and Persistence Behavior

Runtime state includes shared anonymous memory for parsed mount info, capability sets, fsuid/fsgid during mountpoint acquisition, password buffers, generated option strings, current working directory, and mtab lock files. Persistent effects are the kernel mount, optional `/etc/mtab` updates, and symlinked `mount.smb3` behavior through `argv[0]`.

## Dependencies and Integration Points

It depends on libc mount APIs, NSS passwd/group, libcap-ng or libcap/prctl fallbacks, systemd ask-password when enabled, keyring/Kerberos semantics through kernel CIFS options, `resolve_host`, `mtab.c`, and `util.c`. It integrates with `/etc/fstab`, environment variables `PASSWD`, `PASSWD_FD`, `PASSWD_FILE`, `PASSWD2*`, `USER`, and `SUDO_UID`.

## Risks and Edge Cases

This is security-critical. Option parsing mutates a copied option string in place and comma escaping for passwords must remain correct. Privilege separation depends on no pointers in `struct parsed_mount_info`. `set_password` checks `j > pass_length` after writes, which requires careful boundary tests. Mtab writes are legacy and must be skipped for symlinked mtab. The helper constructs a kernel option string bounded to one page; every append path must preserve the limit.

## Test Signals

Tests should cover root and unprivileged fstab mounts, credentials files, password env/file/fd inputs, Kerberos/noauth/guest password suppression, multi-address retry, uppercase retry, `SUDO_UID` cruid fallback, snapshot token conversion, mtab add/delete, fake mounts, systemd ask-password fallback, and static analysis of capability transitions and option bounds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/mount.cifs.c -->
