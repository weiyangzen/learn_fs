## sources/test-tools/kdevops/workflows/linux/refs/static/btrfs-devel.yaml

Purpose: Static ref manifest for the btrfs-devel kernel tree.

Important APIs/types/functions: Provides one `configs` entry mapping label `btrfs-devel` to config symbol `BOOTLINUX_TREE_BTRFS_DEVEL_REF_BTRFSDEVEL`, ref `btrfs-devel`, and help text.

Control flow: Data-only YAML consumed by Kconfig generation or ref selection tooling.

State and persistence: No runtime state; checked-in static metadata.

Dependencies and integration points: Must align with `workflows/linux/Kconfig.btrfs` generated symbols and bootlinux tree selection.

Risks and test signals: Ref names can stale if upstream branches rename. Test by regenerating Kconfig fragments and attempting a clone/checkout.
