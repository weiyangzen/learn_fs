<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get_libvirsh_pool_enabled.sh -->
# sources/test-tools/kdevops/scripts/get_libvirsh_pool_enabled.sh

Purpose: determines whether libvirt storage pool path inference should be enabled for the current working directory.

Important APIs and functions: sources `libvirt_pool.sh`, initializes libvirt-related globals, calls `get_pool_vars`, `virsh_works`, `virsh_get_pool_list`, and `virsh_path_in_pool_list_exists`.

Control flow: derive `BASE_DIR` from `$PWD`, load pool variables, bail out with `n` if `virsh_works` reports no, otherwise gather pool list and print the result of path-in-pool detection.

State and persistence: read-only; uses libvirt/virsh state and current working directory.

Dependencies and integration: bash, `libvirt_pool.sh`, virsh through helper functions. `kconfigs/Kconfig.libvirt` consumes it for `LIBVIRT_STORAGE_POOL_PATH_INFER_ADVANCED`.

Risks: helper function output is the script's output contract; any stderr/stdout noise from helpers can corrupt Kconfig defaults. Path parsing uses `awk -F"/" '{print $2}'`, which only captures the top-level directory. Test signals include stubbing helper functions for virsh success/failure and matching/nonmatching pools.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get_libvirsh_pool_enabled.sh -->
