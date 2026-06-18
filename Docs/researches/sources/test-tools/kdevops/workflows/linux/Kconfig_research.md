## sources/test-tools/kdevops/workflows/linux/Kconfig

Purpose: Configures the bootlinux workflow for cloning, building, installing, and rebooting into selected Linux kernel trees.

Important APIs/types/functions: Major symbols include build-location choices `BOOTLINUX_TARGETS`, `BOOTLINUX_9P`, `BOOTLINUX_BUILDER`; compiler choice; reproducible/clean/ccache options; tree families `BOOTLINUX_LINUS/STABLE/DEV/CUSTOM`; derived `BOOTLINUX_TREE_NAME`, `BOOTLINUX_TREE`, `BOOTLINUX_TREE_REF`; message-id testing via `BOOTLINUX_TEST_MESSAGE_ID`; shallow clone; and A/B baseline/dev ref controls.

Control flow: The file is gated by `BOOTLINUX`. It selects build topology, optional 9p settings, compiler/cache behavior, tree family and sourced tree-specific Kconfigs, custom tree overrides, derived tree/ref values, optional b4 patch application, shallow clone depth, and A/B baseline/dev kernel selection.

State and persistence: Kconfig writes persistent `.config` and YAML-output variables. Runtime state is created by the Makefile/Ansible playbook, not by Kconfig.

Dependencies and integration points: Sources many generated/static Kconfig fragments (`Kconfig.linus`, stable, next, vfs, xfs, modules, etc.). Integrates with CLI variables `LINUX_TREE`, `LINUX_TREE_REF`, `B4_MESSAGE_ID`, libvirt 9p, ccache, and kdevops baseline/dev host groups.

Risks and test signals: Tree/ref derivation is complex and CLI override interaction can be subtle. Test via menuconfig/defconfig, inspect `extra_vars.yaml`, run clone-only targets, and verify baseline/dev refs when A/B testing is enabled.
