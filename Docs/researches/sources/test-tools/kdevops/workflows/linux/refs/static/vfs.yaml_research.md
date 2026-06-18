## sources/test-tools/kdevops/workflows/linux/refs/static/vfs.yaml

Purpose: Static ref manifest for VFS block-size work.

Important APIs/types/functions: Defines `lbs` mapped to `BOOTLINUX_TREE_VFS_REF_LBS` and ref `vfs.blocksize`.

Control flow: Data-only.

State and persistence: Static metadata.

Dependencies and integration points: Consumed by Linux Kconfig generation for VFS tree choices.

Risks and test signals: Branch name is external and may be rebased. Validate checkout and build support for selected test configs.
