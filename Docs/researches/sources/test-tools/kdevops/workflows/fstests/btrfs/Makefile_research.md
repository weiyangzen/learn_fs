## sources/test-tools/kdevops/workflows/fstests/btrfs/Makefile

Purpose: Translates btrfs fstests Kconfig selections into `FSTESTS_ARGS` variables passed into the kdevops Ansible workflow.

Important APIs/types/functions: The API is Make variables appended to `FSTESTS_ARGS`, such as `fstests_btrfs_enables_raid56=True`, `fstests_btrfs_enables_compression_zstd=True`, and `fstests_btrfs_section_nohofspace_zstd=True`.

Control flow: Nested `ifeq (y,$(CONFIG_*))` blocks mirror the Kconfig feature hierarchy. Feature-level enablement gates section-level args so only coherent btrfs coverage combinations are exported.

State and persistence: It does not persist state directly. It derives args from the checked-in or generated `.config` and contributes to `WORKFLOW_ARGS` through the parent fstests Makefile.

Dependencies and integration points: Included by `workflows/fstests/Makefile` when `CONFIG_FSTESTS_BTRFS=y`. Downstream Ansible roles must understand every emitted `fstests_btrfs_*` variable.

Risks and test signals: Typos in variable names silently break provisioning because Make succeeds while Ansible sees missing vars. Compare `make print-vars`/generated `extra_vars.yaml` with expected btrfs section inventory and run a dry provisioning target to verify.
