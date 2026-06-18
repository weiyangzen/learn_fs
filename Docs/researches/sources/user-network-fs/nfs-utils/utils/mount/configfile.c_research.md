# sources/user-network-fs/nfs-utils/utils/mount/configfile.c

Purpose: converts `/etc/nfsmount.conf` entries into effective mount options layered with CLI/fstab options.

Important APIs and data: `conf_get_mntopts(spec, mount_point, mount_opts)` is exported via `mount_config.h`. `conf_parse_mntopts()` adds options from `MountPoint`, `Server`, and global sections. `mountopts_alias()` maps human option names like `background` to `bg`; `mountopts_convert()` expands `k`, `m`, and `g` size suffixes. `default_value()` populates global default version/protocol settings used by network probing.

Control flow: existing options are parsed first and take precedence. The code then applies mountpoint-specific, server-specific, and global options, skipping duplicates, inverses, conflicting `fg`/`bg`, and extra version keys. Boolean false is transformed to `no<opt>` or inverted aliases.

State and persistence: global `config_default_vers`, `config_default_proto`, external `config_default_family`, and file-scope `strict` are mutated during parse. Persistent input is the configured mount options file.

Dependencies and integration: uses nfs-utils conffile, option-list helpers, network protocol/version parsers, and xlog.

Risks: size conversion uses a static buffer and `strtol` into unsigned arithmetic; default option parsing depends on string prefixes. Test signals include precedence order, false/true handling, case-insensitive aliases, version de-duplication, defaultproto/defaultvers side effects, and suffix conversion.
