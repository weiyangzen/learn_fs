# sources/user-network-fs/nfs-utils/support/nfsidmap/libtest.c

Purpose: `libtest.c` is a small manual exerciser for libnfsidmap translation paths. It reads the normal idmap configuration through `nfs4_init_name_mapping(NULL)` and tries principal-to-id, name-to-id, group-list, and id-to-name conversions.

Important APIs and control flow: `main` expects `<user@nfsv4domain> <k5princ@REALM>`, enables debug logging with `nfs4_set_debug(3, NULL)`, initializes mapping, calls `nfs4_gss_princ_to_ids`, `nfs4_name_to_uid`, `nfs4_name_to_gid`, `nfs4_gss_princ_to_grouplist`, `nfs4_uid_to_name`, and `nfs4_gid_to_name`, and exits early after failures when `QUIT_ON_ERROR` is enabled.

State, dependencies, and integration: State is local stack buffers plus a global `conf_path` pointing at `/etc/idmapd.conf`, though initialization is delegated to the library. It depends on installed `nfsidmap.h` and links with `-lnfsidmap`.

Risks and test signals: The file uses old-style `main` without an explicit return type and fixed 32-byte owner output buffers. Useful tests are interactive runs with NSS, static, regex, and GSS principal mappings, including too-small output buffers and missing realm/domain configuration.
