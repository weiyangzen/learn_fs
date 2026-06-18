# sources/user-network-fs/nfs-utils/support/nfsidmap/libnfsidmap.c

Purpose: core NFSv4 name/id mapping library that initializes configuration, discovers the NFSv4 domain, loads translation plugins, and exposes mapping APIs.

Important APIs and data: public functions include `nfs4_init_name_mapping()`, `nfs4_term_name_mapping()`, `nfs4_get_default_domain()`, `nfs4_uid_to_name()`, `nfs4_gid_to_name()`, `nfs4_uid_to_owner()`, `nfs4_gid_to_group_owner()`, `nfs4_name_to_uid()`, `nfs4_name_to_gid()`, `nfs4_owner_to_uid()`, `nfs4_group_owner_to_gid()`, GSS principal mapping variants, `nfs4_set_debug()`, and `nfsidmap_config_get()`. Global plugin arrays `nfs4_plugins` and `gss_plugins` hold dynamically loaded mapping backends.

Control flow: initialization loads config with `conf_init_file()`, obtains `Domain` or derives it from hostname/DNS `_nfsv4idmapdomain` TXT record, loads local realms, reads `[Translation] Method` or defaults to `nsswitch`, optionally loads `GSS-Methods`, and resolves configured nobody user/group. `load_translation_plugin()` first tries `dlopen("<method>.so")` via the search path, verifies the plugin init symbol, falls back to `PATH_PLUGINS/<method>.so`, calls plugin init and optional plugin `.init`, then stores the handle and function table. The `RUN_TRANSLATIONS` macro initializes lazily and invokes each plugin function until one returns other than `-ENOENT`.

State and persistence: process-global default domain, plugin arrays, nobody UID/GID, logging callback/verbosity, and config path. Persistent inputs are idmapd.conf, DNS/NSS resolver state, plugin shared objects, password/group databases, and plugin-specific backing stores.

Dependencies and integration: depends on `conffile.c`, resolver APIs, `dlopen()`, libnfsidmap plugin ABI, local realm helpers from `nfsidmap_common.c`, and NSS password/group APIs. Used by kernel idmapping helpers and user-space NFSv4 ACL/id conversion.

Risks: global initialization is not synchronized and comments note reload limitations. DNS parsing uses low-level resolver message walking and trusts the first TXT answer. `id_as_chars()` accepts numeric strings with trailing junk because it does not inspect `strtol()` end pointer. Owner/group fallback writes numeric IDs with `sprintf()` without checking the caller buffer length. Plugin unload assumes plugin arrays are complete and can call `dlclose()` while plugin data may still be referenced elsewhere.

Test signals: explicit domain, DNS TXT domain, fallback default domain, Method and GSS-Methods ordering, plugin load fallback path, plugin init failure cleanup, nobody configured/missing, numeric owner fallback, nobody fallback, each mapping API continuing on `-ENOENT`, and term/reinit behavior.
