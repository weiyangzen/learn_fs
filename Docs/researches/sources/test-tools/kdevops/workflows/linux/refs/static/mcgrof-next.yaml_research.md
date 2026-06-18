## sources/test-tools/kdevops/workflows/linux/refs/static/mcgrof-next.yaml

Purpose: Static ref manifest for mcgrof large-block branches based on linux-next.

Important APIs/types/functions: Entries `lbs` and `lbs-nobdev` map to `BOOTLINUX_TREE_MCGROF_NEXT_REF_*` and refs `large-block-next`/`large-block-nobdev`.

Control flow: Data-only.

State and persistence: Static YAML metadata.

Dependencies and integration points: Feeds bootlinux Kconfig ref choices for development kernels.

Risks and test signals: next-based branches move or rebase often. Test checkout and build config availability before long workflow runs.
