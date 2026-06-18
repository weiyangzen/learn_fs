<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/krb5_util.c -->
# sources/user-network-fs/nfs-utils/utils/gssd/krb5_util.c

## Purpose
This file manages Kerberos credential caches, keytab principal selection, machine credential refresh, user credential cache selection, service-ticket cleanup, and encryption-type policy for gssd.

## APIs And Control Flow
User credential flow starts in `gssd_setup_krb5_user_gss_ccache`: expand `%U` directory patterns, scan for `krb5cc` files/dirs, reject wrong owners and expired/corrupt caches, prefer configured realms and newest mtime, and select the cache with `gss_krb5_ccache_name`. Machine credential flow uses `gssd_refresh_krb5_machine_credential_internal`: resolve the keytab, find a principal for `$`, `root`, `nfs`, or `host` service names across target/preferred/default realms, create or find a principal-list entry, choose FILE or MEMORY ccache, and obtain/refresh init creds from the keytab. `gssd_get_krb5_machine_cred_list` refreshes cached principals and returns ccname strings for context creation. Optional enctype logic intersects kernel, config, and library permitted enctypes in library order and applies them with `gss_set_allowable_enctypes`.

## State, Dependencies, And Integration
State includes the global principal list, `ple_lock`, per-principal ccname/endtime/refcount, allowed/kernel/library enctype arrays, and global config from `gssd.c`. Dependencies are Kerberos krb5 APIs, GSSAPI Kerberos extensions, nfs.conf, DNS canonicalization, keytab and ccache files, and gssd logging.

## Risks And Test Signals
Risks include complex lock/refcount behavior, credential cache ownership and expiry edge cases, hostname canonicalization and AD machine-account assumptions, stale machine cache destruction on shutdown, global enctype cache invalidation, and service-ticket removal using fixed `nfs/<name>`. Test user cache selection, preferred realm ordering, FILE vs MEMORY caches, keytab service matching, force renew, expired/corrupt caches, allowed-enctype intersections, bad service ticket removal, and concurrent refresh/list operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/krb5_util.c -->
