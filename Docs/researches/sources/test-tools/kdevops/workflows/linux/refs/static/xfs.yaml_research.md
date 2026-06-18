## sources/test-tools/kdevops/workflows/linux/refs/static/xfs.yaml

Purpose: Static ref manifest for the XFS development tree.

Important APIs/types/functions: One entry `for-next` maps to `BOOTLINUX_TREE_XFS_REF_NEXT` and ref `for-next`.

Control flow: Data-only.

State and persistence: Static YAML metadata.

Dependencies and integration points: Used by XFS Linux Kconfig generation and bootlinux tree selection.

Risks and test signals: Moving `for-next` can change behavior across runs. Test by recording checked-out commit IDs and verifying config availability.
