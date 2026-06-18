## sources/test-tools/kdevops/workflows/linux/refs/static/stable.yaml

Purpose: Static ref manifest for stable Linux releases and stable branches.

Important APIs/types/functions: Lists historical tags and longterm branch refs mapped to `BOOTLINUX_TREE_STABLE_REF_*`, including `linux-6.1.y` and `linux-6.6.y`.

Control flow: Data-only list.

State and persistence: Static YAML metadata.

Dependencies and integration points: Feeds stable Kconfig generation and bootlinux ref selection.

Risks and test signals: Stable branch coverage may lag current maintained series. Test generation, checkout, and whether inferred configs exist for selected stable refs.
