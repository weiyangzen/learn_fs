## sources/test-tools/kdevops/workflows/fstests/tmpfs/Makefile

Purpose: Emits tmpfs fstests Ansible arguments from tmpfs Kconfig selections.

Important APIs/types/functions: Adds `fstests_tmpfs_enable`, `fstests_tmpfs_section_default`, `fstests_tmpfs_enable_noswap`, `fstests_tmpfs_section_noswap_huge_*`, `fstests_tmpfs_enable_huge`, and `fstests_tmpfs_section_huge_*` to `FSTESTS_ARGS`.

Control flow: Flat conditional checks append args for default, noswap, noswap huge policies, and huge policies. Comments note this Makefile could shrink if Kconfig gains direct extra-vars YAML output.

State and persistence: No state beyond derived Make variables.

Dependencies and integration points: Included by parent fstests Makefile. The Ansible side must interpret these booleans into tmpfs config sections/mount options.

Risks and test signals: Because all args are optional booleans, missing a true arg changes coverage silently. Inspect generated extra vars and host config sections for each selected tmpfs mode.
