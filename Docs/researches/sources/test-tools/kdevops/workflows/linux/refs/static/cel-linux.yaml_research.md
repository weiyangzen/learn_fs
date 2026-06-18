## sources/test-tools/kdevops/workflows/linux/refs/static/cel-linux.yaml

Purpose: Static ref manifest for the cel-linux NFS server development tree.

Important APIs/types/functions: Defines `next`, `fixes`, `testing`, and `custom` entries mapped to `BOOTLINUX_TREE_CEL_LINUX_REF_*` symbols and refs such as `nfsd-next`.

Control flow: Data-only selection list; custom entry delegates ref to `BOOTLINUX_TREE_CEL_LINUX_CUSTOM_REF_NAME`.

State and persistence: Static metadata only.

Dependencies and integration points: Consumed by Linux Kconfig fragment generation and bootlinux tree/ref selection.

Risks and test signals: Branch names are external contracts with the maintainer tree. Validate by generating Kconfig and checking out each static ref.
