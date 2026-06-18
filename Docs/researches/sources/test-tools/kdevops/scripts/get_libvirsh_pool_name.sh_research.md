<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get_libvirsh_pool_name.sh -->
# sources/test-tools/kdevops/scripts/get_libvirsh_pool_name.sh

Purpose: returns the libvirt storage pool name whose path matches the current working directory's top-level base path, or `default` when inference is unavailable.

Important APIs and functions: sources `libvirt_pool.sh`; calls `get_pool_vars`, `virsh_works`, `virsh_get_pool_list`, `virsh_path_in_pool_list_exists`, and `virsh_path_pool_list_name`.

Control flow: initialize helper globals, load pool vars, return `default` if virsh is unavailable, collect pool list, return `default` if no pool path matches, otherwise print the matched pool name.

State and persistence: read-only against libvirt state and cwd.

Dependencies and integration: bash, libvirt helper functions, virsh. `kconfigs/Kconfig.libvirt` uses it as an inferred storage pool name default.

Risks: relies on sourced functions emitting exactly one clean value. Current-directory matching by top-level path may be too coarse on systems with multiple pools under the same prefix. Source path and variable expansions are mostly unquoted. Test signals include stubs for no virsh, no match, and match cases, plus cwd path variations.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get_libvirsh_pool_name.sh -->
