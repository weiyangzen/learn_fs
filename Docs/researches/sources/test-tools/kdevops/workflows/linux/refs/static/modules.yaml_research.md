## sources/test-tools/kdevops/workflows/linux/refs/static/modules.yaml

Purpose: Static ref manifest for modules tree testing.

Important APIs/types/functions: One entry `modules-next` maps to `BOOTLINUX_TREE_MODULES_REF_NEXT` and ref `modules-next`.

Control flow: Data-only.

State and persistence: Static metadata.

Dependencies and integration points: Used by generated modules Kconfig and bootlinux tree selection.

Risks and test signals: Ref availability is the only functional risk. Validate with `git ls-remote`/clone checkout.
