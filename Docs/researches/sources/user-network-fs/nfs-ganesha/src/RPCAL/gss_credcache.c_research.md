# sources/user-network-fs/nfs-ganesha/src/RPCAL/gss_credcache.c

Purpose: manages Kerberos/GSS machine credential acquisition and cleanup for Ganesha callbacks, including keytab discovery, principal caching, credential cache creation, and supported-mechanism checks.

Important APIs and types: `gssd_init_cred_cache()`, `gssd_shutdown_cred_cache()`, `gssd_refresh_krb5_machine_credential()`, `gssd_check_mechs()`, `gssd_clear_cred_cache()`, `struct gssd_k5_kt_princ`, `ccachesearch[]`, `gssd_get_single_krb5_cred()`, `find_keytab_entry()`, `gssd_search_krb5_keytab()`, and Kerberos/GSS functions such as `krb5_get_init_creds_keytab()`, `krb5_cc_initialize()`, and `gss_indicate_mechs()`.

Control flow: refresh initializes a krb5 context, resolves the configured keytab, finds or creates a principal-list entry either from an explicit `ple` or by hostname/service keytab lookup, then obtains credentials if the cached ccache is missing/expired. Keytab selection tries AD machine account, `root`, `nfs`, and `host` by default unless a specific service is requested; it tries target realm, default realm, exact host principals, and any-instance service principals. Successful credentials are stored in a `MEMORY:` or `FILE:` ccache under `ccachesearch[0]`, and the GSS mechanism is pointed at that ccache via `gss_krb5_ccache_name()` or `KRB5CCNAME`.

State and persistence: global `gssd_k5_kt_princ_list` caches principal, realm, ccache name, and ticket end time under `ple_mtx`. FILE ccaches may persist on disk until cleared or overwritten; MEMORY ccaches are process-local. `gssd_clear_cred_cache()` walks the global list, destroys krb5 ccaches when a context can be created, and frees entries.

Dependencies and integration points: depends on MIT/Heimdal Kerberos compatibility macros, `nfs_param.krb5_param.keytab`, `ccachesearch`, name resolution helpers, Ganesha memory/logging utilities, and callback/authentication code that needs machine credentials.

Risks: global principal entries are protected only while finding/adding/clearing entries; individual `ple` updates in credential refresh are not separately locked. `ccachesearch[0]` must be initialized and writable for FILE caches. Hostname canonicalization and realm lookup can block or fail DNS. Environment-variable ccache selection is process-global. Cleanup proceeds even if ccache destruction fails, which avoids memory leaks but can leave FILE ccaches behind.

Test signals: MIT and Heimdal builds, keytab with exact host principal, any-instance fallback, AD machine-account fallback, missing keytab, expired versus valid cached creds, MEMORY and FILE cache modes, ccache cleanup, DNS failure, and `gss_indicate_mechs()` failure/empty set.
