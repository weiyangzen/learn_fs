## sources/test-tools/kdevops/workflows/linux/refs/static/linus.yaml

Purpose: Static ref manifest for Linus tree selections.

Important APIs/types/functions: Lists `master` and several release-candidate tags mapped to `BOOTLINUX_TREE_LINUS_REF_*` symbols.

Control flow: Data-only list used by generation tooling.

State and persistence: Static metadata only.

Dependencies and integration points: Integrated with `Kconfig.linus` and `LATEST_BOOTLINUX_TREE_REF` selection.

Risks and test signals: RC tags are historical and may not represent current desired test coverage. Test by regenerating Kconfig and checking `git ls-remote` for every ref.
