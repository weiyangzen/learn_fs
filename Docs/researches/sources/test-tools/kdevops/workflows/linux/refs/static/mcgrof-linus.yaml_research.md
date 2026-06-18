## sources/test-tools/kdevops/workflows/linux/refs/static/mcgrof-linus.yaml

Purpose: Static ref manifest for mcgrof large-block branches based on Linus's tree.

Important APIs/types/functions: Defines `lbs` and `lbs-nodeb` entries with symbols `BOOTLINUX_TREE_MCGROF_LINUS_REF_LBS*` and refs `large-block-linus` and `large-block-linus-nobdev`.

Control flow: Data-only.

State and persistence: Static YAML metadata.

Dependencies and integration points: Used by Linux Kconfig generation and bootlinux tree checkout.

Risks and test signals: Help text mentions sector-size compatibility; checkout and kernel config support should be verified for both branches.
