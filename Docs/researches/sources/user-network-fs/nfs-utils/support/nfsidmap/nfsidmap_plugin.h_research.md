# sources/user-network-fs/nfs-utils/support/nfsidmap/nfsidmap_plugin.h

Purpose: `nfsidmap_plugin.h` is the private ABI contract used by libnfsidmap translation plugins.

Important APIs and types: `struct trans_func` names a plugin and provides callbacks for initialization, GSS principal-to-ids, name-to-uid/gid, uid/gid-to-name, and GSS group-list lookup. It exports `idmap_verbosity`, `idmap_log_func`, `nfsidmap_conf_path`, `nfsidmap_config_get`, and the plugin entry point `libnfsidmap_plugin_init`. `IDMAP_LOG` centralizes verbosity-based logging, and `UNUSED` helps keep callback signatures uniform.

State, dependencies, and integration: Runtime state is owned by libnfsidmap and each plugin; this header only binds them. Bundled plugins `nss`, `regex`, `static`, and `umich_ldap` each return a `trans_func`.

Risks and test signals: This ABI is pointer-table based, so signature drift breaks dynamically loaded plugins. Callbacks return negative errno-style values by convention. Tests should compile all plugins, load them through libnfsidmap, and verify missing callbacks or failed init are handled.
