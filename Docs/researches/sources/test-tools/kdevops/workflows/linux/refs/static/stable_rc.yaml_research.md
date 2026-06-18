## sources/test-tools/kdevops/workflows/linux/refs/static/stable_rc.yaml

Purpose: Static ref manifest for stable release-candidate queue branches.

Important APIs/types/functions: Entries map queue branches `queue/5.4` through `queue/6.15` to `BOOTLINUX_TREE_STABLE_RC_REF_QUEUE_*` symbols.

Control flow: Data-only.

State and persistence: Static YAML metadata.

Dependencies and integration points: Used by stable-rc Kconfig generation and bootlinux tree/ref selection.

Risks and test signals: Queue branches are moving targets and may force rebuild variability. Test by recording exact commit IDs during workflow runs.
