# sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/ccache.yml

This task file configures kdevops-managed ccache for bootlinux builds. When ccache and managed mode are enabled, it creates `topdir_path/.ccache` and `bootlinux_ccache_dir`, renders `ccache.conf.j2`, and prints a summary of enabled mode, config path, cache directory, and maximum size.

Important APIs are `file`, `template`, and `debug`. Persistent state includes the ccache directory tree and generated config. Integration points are defaults that inject `CCACHE_CONFIGPATH` and `CC` into build environments, plus the distro dependency files that install `ccache`. Risks include directory mode `0755` exposing cache metadata, undefined `bootlinux_ccache_dir` or `bootlinux_ccache_max_size`, and only configuring managed mode while system-wide mode depends on external setup. Test signals should render the config and run a tiny make invocation with the expected `CCACHE_CONFIGPATH`.
