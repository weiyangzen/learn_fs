## sources/test-tools/kdevops/workflows/linux/refs/static/kdevops-linus.yaml

Purpose: Static ref manifest for kdevops branches based on Linus's tree.

Important APIs/types/functions: Provides `minorder` mapped to `BOOTLINUX_TREE_KDEVOPS_LINUS_REF_LBS_MINORDER` and ref `large-block-minorder`.

Control flow: Data-only.

State and persistence: Static YAML metadata.

Dependencies and integration points: Feeds Linux Kconfig ref generation for kdevops-maintained trees.

Risks and test signals: Single-entry manifests are easy to overlook during branch cleanup. Validate checkout of `large-block-minorder`.
