## sources/test-tools/kdevops/workflows/linux/refs/static/jlayton-linux.yaml

Purpose: Static ref manifest for Jeff Layton's Linux tree.

Important APIs/types/functions: Entries map `kdevops`, `iversion`, and `custom` to `BOOTLINUX_TREE_JLAYTON_LINUX_REF_*` symbols and refs.

Control flow: Data-only; custom ref uses `BOOTLINUX_TREE_JLAYTON_LINUX_CUSTOM_REF_NAME`.

State and persistence: Static YAML metadata.

Dependencies and integration points: Integrated into generated Linux tree Kconfig and bootlinux ref selection.

Risks and test signals: Ref availability can drift. Test by generated Kconfig symbol presence and clone checkout of `kdevops` and `iversion-next`.
