# sources/user-network-fs/nfs-utils/utils/mount/mount_config.h

Purpose: compile-time abstraction for optional mount configuration file support.

Important APIs: when `MOUNT_CONFIG` is defined, `mount_config_init(program)` opens xlog and reads `MOUNTOPTS_CONFFILE` (default `/etc/nfsmount.conf`), while `mount_config_opts(spec, mount_point, mount_opts)` calls `conf_get_mntopts()`. Without `MOUNT_CONFIG`, both are no-op/pass-through inline functions.

Control flow and integration: `mount.c` and `mount_libmount.c` call these unconditionally, allowing the same frontend code to build with or without config-file support.

State and persistence: the enabled path reads global config into conffile state and may indirectly update global default protocol/version state in `configfile.c`.

Dependencies: enabled path depends on `conffile.h` and `xlog.h`; disabled path has no runtime dependencies.

Risks and tests: behavior changes substantially with the compile flag. Test signals include config-enabled and config-disabled builds, default file path override, and preserving caller option strings when disabled.
