# sources/user-network-fs/samba/source3/wscript

## Purpose

This Waf script defines the configure-time policy for Samba's `source3` tree. It adds user-facing options for optional subsystems, probes the host OS and dependency surface, decides which features and VFS/passdb/auth/idmap modules are available, and writes the resulting `include/config.h` plus Waf environment values consumed by `source3/wscript_build` and recursive subdirectories.

## Important APIs, Functions, And Data

The two top-level entry points are `options(opt)` and `configure(conf)`. `options()` exposes module placement controls through `--with-static-modules` and `--with-shared-modules`, plus many `samba_add_onoff_option()` toggles such as winbind, ADS, CUPS, PAM, ACLs, quotas, clustering, CephFS, GlusterFS, Spotlight, WSP, regedit, winexe, fake kaserver, profiling, and libarchive.

`configure(conf)` is the main body. It initializes `default_static_modules`, `default_shared_modules`, `required_static_modules`, `forced_static_modules`, and `forced_shared_modules`, then mutates them as feature checks succeed. It relies on Waf/Samba helpers such as `CHECK_HEADERS`, `CHECK_FUNCS`, `CHECK_FUNCS_IN`, `CHECK_CODE`, `CHECK_CFG`, `CHECK_LIB`, `CHECK_STRUCTURE_MEMBER`, `SET_TARGET_TYPE`, `DEFINE`, `CONFIG_SET`, and `SAMBA_CONFIG_H`.

Notable configure outputs include `HAVE_INOTIFY`, `HAVE_KERNEL_OPLOCKS_LINUX`, `HAVE_FAM`, `HAVE_CUPS`, `HAVE_KRB5`, `HAVE_ADS`, `WITH_WINBIND`, `WITH_PAM`, `WITH_PROFILE`, `WITH_QUOTAS`, `CLUSTER_SUPPORT`, `HAVE_CEPH`, `HAVE_GLUSTERFS`, `HAVE_LIBURING`, `WITH_WSP`, `WITH_SPOTLIGHT`, `STRING_STATIC_MODULES`, `STRING_SHARED_MODULES`, `static_decl_<prefix>`, and `static_init_<prefix>(mem_ctx)`.

## Control Flow

Configuration begins with broad libc/kernel probes, then feature-specific blocks. Early code detects platform primitives such as headers, stat fields, file locking, sendfile variants, inotify, Linux leases, netlink, filesystem hints, timestamps, quotas, ACLs, and credential-changing syscalls. Optional library blocks either define usable target types or create empty target placeholders so later dependency declarations can stay uniform.

The ADS/Kerberos block is a central gate. Unless `--without-ads` is used, it checks Kerberos enctypes, ticket APIs, keytab/free functions, GSS PAC extraction, lucid context export, and LDAP transport wrapping. If required Kerberos or LDAP capability is absent, it disables ADS or fails when ADS was explicitly requested. This output directly affects whether `HAVE_KRB5` and `HAVE_ADS` are available to the build.

Late in the script, module lists are populated from defaults and feature gates. Explicit `--with-static-modules` and `--with-shared-modules` are converted to lists, `pdb_ldap` is normalized to `pdb_ldapsam`, `ALL`, `!DEFAULT`, `!FORCED`, and `!module` are applied, and hard constraints prevent required-static modules from being shared or forced modules from moving to the wrong side. The final lists are grouped by prefixes `vfs`, `pdb`, `auth`, `nss_info`, `charset`, `idmap`, and `gpext`, exported into `conf.env`, and used to generate static init macros.

## State And Persistence

This script does not persist runtime application state. Its persistent outputs are build state: Waf `conf.env`, generated configure defines in `include/config.h`, target type declarations for missing optional libraries, and module list strings/macros compiled into source3. The script also controls whether recursive build files will build modules by setting `conf.env['static_modules']`, `conf.env['shared_modules']`, and per-prefix lists such as `VFS_STATIC`/`VFS_SHARED`.

## Dependencies And Integration Points

It depends on Waf's `Options`, `Logs`, and `Errors`, Samba's wafsamba helpers, `build.charset`, `samba_utils.TO_LIST`, and `samba3`. It integrates with `source3/wscript_build` through environment variables such as `with_avahi`, `with_ctdb`, `dmapi_lib`, `legacy_quota_libs`, `with_wsp`, and `spotlight_backend_es`. It also integrates with recursive module `wscript_build` files through `SAMBA3_IS_ENABLED_MODULE()` and the generated static/shared module env lists.

Key external dependencies include POSIX libc, Kerberos/GSSAPI, LDAP, CUPS, PAM, ACL libraries, FAM, libarchive, libevent, DMAPI variants, capabilities, tirpc, CephFS, GlusterFS, liburing, ncurses, mingw, OpenSSL/libcrypto DES, AFS headers, DBus for `vfs_snapper`, gettext/intltool, flex/bison/Jansson/Unicode normalization for Spotlight, and kernel-specific filesystem APIs.

## Risks And Edge Cases

The file has many execute-time configure tests; cross-compilation and restricted build sandboxes can change outcomes. Optional dependencies sometimes default to required behavior, for example libarchive is required by default and ACL support fails the build unless disabled. ADS is particularly sensitive to Kerberos/GSSAPI feature coverage. Module resolution is order-independent by design, but incorrect entries in `--with-static-modules` or `--with-shared-modules` can conflict with required/forced placement and raise Waf errors. Empty target placeholders are useful but can hide disabled optional features until link or runtime behavior is inspected.

## Test Signals

Useful validation signals are successful `./configure`/Waf configure on representative platforms, generated `include/config.h` defines, logged static/shared module lists, and builds of optional feature combinations. Selftest and developer builds exercise extra modules. Focused test matrices should cover `--without-ads`, explicit ADS failure, ACL disabled/enabled, libarchive disabled with selftest, quota/sendfile variants, CephFS/GlusterFS presence and absence, Spotlight backends, and static/shared module override syntax.
