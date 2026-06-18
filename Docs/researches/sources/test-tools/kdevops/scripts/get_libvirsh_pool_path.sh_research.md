<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get_libvirsh_pool_path.sh -->
# sources/test-tools/kdevops/scripts/get_libvirsh_pool_path.sh

Purpose: returns an inferred libvirt storage pool path for the current kdevops checkout, falling back to local/default paths when virsh or matching pools are unavailable.

Important APIs and functions: sources `libvirt_pool.sh`; calls `get_pool_vars`, `virsh_works`, `virsh_get_pool_list`, `virsh_path_in_pool_list_exists`, and `virsh_path_pool_list_path`.

Control flow: if virsh does not work, print `$(pwd)/default`; if virsh works but the current base path is not in any pool list, print `/var/lib/libvirt/images`; otherwise print the matched pool path.

State and persistence: read-only; output depends on cwd and libvirt pool state.

Dependencies and integration: bash, libvirt helpers, virsh. `kconfigs/Kconfig.libvirt` uses it for `LIBVIRT_STORAGE_POOL_PATH_INFER_ADVANCED`.

Risks: fallback behavior differs between virsh-unavailable and no-match cases, which may surprise users. Unquoted source path and `pwd` output can fail with spaces. Helper stdout purity matters. Test signals include helper stubs for each branch and Kconfig default validation with paths containing spaces.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get_libvirsh_pool_path.sh -->
