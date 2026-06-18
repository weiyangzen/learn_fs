# sources/user-network-fs/samba/source3/wscript_build

## Purpose

This Waf build script declares the `source3` build graph. It maps source3 libraries, subsystems, binaries, Python extension modules, tests, generated build options, and recursive subdirectories into Samba build targets. It consumes the configure results from `source3/wscript` and other top-level checks to decide which source files and targets are included.

## Important APIs, Functions, And Targets

The file is declarative and uses Waf/Samba build methods on `bld`: `SAMBA_BLDOPTIONS`, `SETUP_BUILD_GROUPS`, `SAMBA3_LIBRARY`, `SAMBA3_SUBSYSTEM`, `SAMBA3_BINARY`, `SAMBA_BINARY`, `SAMBA_LIBRARY`, `SAMBA_SUBSYSTEM`, `SAMBA3_PYTHON`, `RECURSE`, `ENFORCE_GROUP_ORDERING`, and `CHECK_PROJECT_RULES`.

Core library/subsystem declarations include `netapi`, `gse`, `msrpc3`, `AVAHI`, `GROUPDB`, `TLDAP`, `samba-passdb`, `pdb`, `SMBREGISTRY`, `REG_FULL`, `KRBCLIENT`, `samba3util`, `samba-cluster-support`, `TDB_LIB`, `samba3core`, `auth_generic`, `libsmb`, `secrets3`, `smbldap`, `ads`, `SMBCONF_PARAM`, `smbconf`, `sysquotas`, `smbd_base`, `LOCKING`, `PROFILE`, printing subsystems, `LIBNET`, `LIBNMB`, RPC client helpers, `samba3-util`, `CHARSET3`, and error mapping subsystems.

Binary and test targets include `smbd/smbd`, `client/smbclient`, `smbspool`, `smbspool_krb5_wrapper`, `smbspool_argv_wrapper`, `smbconftort`, `test_tldap`, `test_registry_regfio`, `test_adouble`, `test_mdsparser_es`, `versiontest`, `timelimit`, `vlp`, `samba-bgqd`, and `spotlight2es`. Python extension modules include `pysmbd`, `pylibsmb`, `pymdscli`, and `pys3smbconf`.

## Control Flow

The build starts by generating `smbd/build_options.c` and setting build groups. It then declares low-level libraries and subsystems, higher-level server/client components, binaries, Python bindings, and finally recurses into subdirectories such as `auth`, `libgpo/gpext`, `librpc`, `libsmb`, `modules`, `param`, `passdb`, `rpc_server`, `script`, `winbindd`, examples, utilities, `nmbd`, and torture tests.

The script composes several target source lists conditionally. `SAMBA_CLUSTER_SUPPORT_SOURCES` and dependencies switch between CTDB implementations and dummy cluster support based on `bld.env.with_ctdb`. `NOTIFY_SOURCES` and `NOTIFY_DEPS` add inotify and FAM notification implementations when configure set the corresponding variables. `SMB1_SOURCES` is included only when `WITH_SMB1SERVER` is configured. `PROFILE` switches between real profiling and a dummy source based on `WITH_PROFILE`.

## State And Persistence

No runtime state is stored here. The file produces build-system state: target declarations, dependency edges, install paths, ABI metadata, public headers, pkg-config files, selftest-only flags, and recursive traversal order. Some targets become empty or disabled indirectly through configure variables such as `HAVE_LDAP`, `HAVE_CUPS`, `HAVE_INOTIFY`, `SAMBA_FAM_LIBS`, `WITH_SMB1SERVER`, `WITH_PROFILE`, `HAVE_CEPH`, and `spotlight_backend_es`.

## Dependencies And Integration Points

This script is tightly coupled to `source3/wscript` for configured feature variables and module decisions. It also depends on common Samba build helpers, generated NDR targets, Kerberos/GSSAPI libraries, LDAP, talloc/tevent/tdb, DB wrap libraries, CUPS, archive, Jansson, cmocka, Python embed helper names, and many internal source3/source4 subsystems.

Important integration points are `gse` depending on `krb5samba gensec smbconf KRBCLIENT secrets3`, `msrpc3` depending on GENSEC and Schannel/NTLM pieces, `libsmb` depending on `auth_generic`, `KRBCLIENT`, SPNEGO parsing, CLDAP, and SMB client common code, `ads` depending on LDAP/Kerberos/RPC/netlogon/passdb, and `smbd_base` depending on VFS, passdb, RPC, locking, leases, notification, quotas, and SMB1/SMB2 server source sets.

## Risks And Edge Cases

Because the file is a large dependency graph, regressions often appear as link-order issues, missing generated targets, unexpected enabled/disabled optional subsystems, or circular dependency problems. Comments explicitly warn that `smbconf` should be the only direct consumer of some registry/config subsystems to avoid cycles, and that `secrets3` must not depend on high-level PDB code. Conditional source concatenation means configure variables must be set consistently; missing empty target placeholders from configure can break otherwise optional dependency edges.

## Test Signals

Signals include a clean Waf build, target availability for configured options, `CHECK_PROJECT_RULES()` success, selftest targets building only under `for_selftest`, ABI checks for public libraries, successful recursive builds in all listed subdirectories, and focused link tests for `smbd`, `smbclient`, `ads`, `gse`, `smbd_base`, notification variants, CUPS-dependent wrappers, Spotlight ES tests, and Python extension modules.
