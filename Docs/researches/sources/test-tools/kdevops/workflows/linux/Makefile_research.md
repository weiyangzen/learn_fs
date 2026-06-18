## sources/test-tools/kdevops/workflows/linux/Makefile

Purpose: Converts bootlinux Kconfig into Ansible arguments and defines Make targets for kernel clone, build, install, deploy, uninstall, reboot, uname, and optional CXL module workflows.

Important APIs/types/functions: Uses `BOOTLINUX_ARGS`, `BOOTLINUX_LIMIT`, `LINUX_CLONE_DEFAULT_TYPE`, `LINUX_DYNAMIC_RUNTIME_VARS`, `HELP_TARGETS`, and targets `linux`, `linux-baseline`, `linux-dev`, `linux-mount`, `linux-deploy`, `linux-build`, `linux-install`, `linux-uninstall`, `linux-clone-*`, `linux-grub-setup`, `linux-reboot`, `uname`, and `linux-cxl`.

Control flow: Derives tree URL/name/ref/config, appends kernel build vars, shallow clone depth, make override, b4 message-id vars, 9p vars, and CXL test flag. If knfsd setup is enabled, `BOOTLINUX_LIMIT` includes `nfsd`. `linux` either fans into baseline/dev targets for A/B different refs or runs one playbook over the selected host limit.

State and persistence: Reads Kconfig-generated variables and may read `KVER` for uninstall. Runtime writes occur through Ansible: clones, builds, installs, GRUB changes, reboots, and saved kernel artifacts.

Dependencies and integration points: Depends on `KDEVOPS_PLAYBOOKS_DIR`, `bootlinux.yml`, inventory nodes, `extra_vars.yaml`, and configuration symbols from linux Kconfig.

Risks and test signals: Playbook tags must match role tag names; wrong host limits can skip NFS server kernel updates. Test with `make linux-clone`, `make linux-build`, `make uname`, and A/B baseline/dev invocations.
