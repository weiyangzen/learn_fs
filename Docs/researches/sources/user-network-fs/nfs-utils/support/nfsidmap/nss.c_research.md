# sources/user-network-fs/nfs-utils/support/nfsidmap/nss.c

Purpose: `nss.c` implements the `nsswitch` idmap plugin, translating NFSv4 owner strings and Kerberos principals through local libc NSS passwd/group databases.

Important APIs and control flow: `nss_uid_to_name` and `nss_gid_to_name` call `getpwuid_r`/`getgrgid_r` and format `local@domain` through `write_name`. `nss_name_to_uid` strips the default domain, then uses `getpwnam_r`. Group lookup supports `No-Strip` and optional `Reformat-Group`, with `_nss_name_to_gid` trying domain-stripped, raw, or `DOMAIN\name` formats. `nss_gss_princ_to_ids` validates `krb5`, checks principal realm against `Local-Realms`, then maps the local principal name; `nss_gss_princ_to_grouplist` calls `getgrouplist`.

State, dependencies, and integration: The plugin initializes `idmapd.conf`, caches the default domain in a static buffer, uses shared policy helpers, and returns `nss_trans` from `libnfsidmap_plugin_init`.

Risks and test signals: Realm comparison is case-sensitive, buffers grow on `ERANGE` in some paths but not all, and `nss_gss_princ_to_grouplist` returns the initialized `ret` on success unless `getgrouplist` fails. Tests should cover realm rejection, domain stripping, group reformatting, large NSS records, and group-list size handling.
