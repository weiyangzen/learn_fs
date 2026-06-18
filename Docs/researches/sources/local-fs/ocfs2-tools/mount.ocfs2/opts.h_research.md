# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/opts.h

Defines private mount option bits and option-mask policy.

It reserves high bits for helper-only options such as `MS_NOAUTO`, `MS_USERS`, `MS_USER`, `MS_OWNER`, `MS_GROUP`, `MS_PAMCONSOLE`, `_netdev`, comments, and loop handling. `MS_NOSYS` excludes helper-only options from `mount(2)`, `MS_NOMTAB` excludes selected flags from mtab, and secure defaults are defined for user/owner mounts.

It declares `parse_opts()` and `fix_opts_string()`.
