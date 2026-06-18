# sources/user-network-fs/nfs-utils/support/nfsidmap/nfsidmap_private.h

Purpose: `nfsidmap_private.h` exposes helper declarations and private structures shared only between libnfsidmap and bundled plugins.

Important APIs and types: It declares common-helper functions from `nfsidmap_common.c`, `idtypes` flags for user/group paths, `libnfsidmap_plugin_init_t`, and `struct mapping_plugin`, which holds a dynamic-library handle and returned `struct trans_func *`.

State, dependencies, and integration: It includes `conffile.h` and is included by plugin implementations and the core library. Durable state is not stored here, but the `mapping_plugin` layout mirrors dynamic plugin loading state in libnfsidmap.

Risks and test signals: The header has no guard in this snapshot and is not suitable for external consumers despite containing ABI-sensitive structures. Tests should build all bundled plugins and libnfsidmap together, verify callback dispatch through `mapping_plugin`, and cover plugin unload cleanup.
