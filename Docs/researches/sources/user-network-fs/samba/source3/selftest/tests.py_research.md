# sources/user-network-fs/samba/source3/selftest/tests.py

Purpose: generates the Samba 3 selftest suite plan consumed by `selftest.pl`. It enumerates blackbox scripts, smbtorture suites, RPC matrices, feature-gated tests, and environment-specific command lines.

Important functions and APIs: imports `selftesthelpers` functions such as `plantestsuite`, `planpythontestsuite`, `plansmbtorture4testsuite`, `binpath`, `samba3srcdir`, and command paths (`smbclient3`, `smbtorture3`, `smbtorture4`, `wbinfo`, `net`, `smbcontrol`, `timelimit`). Local `plansmbtorture4testsuite()` selects the target (`samba3`, `samba4`, or `samba4-ntvfs`) based on environment naming. `compare_versions()` supports Linux kernel feature gating. `is_module_enabled()` checks configured static/shared module lists.

Control flow: reads `config.h` feature data, derives booleans for kernel oplocks, inotify, ldwrap, pthreadpool, cluster support, and QUIC wrapper support, then emits hundreds of test registrations. The files in this subset are wired in several clusters: vfstest runners around lines 598-600; username-map and keytab tests around 617 and 678-687; winbind trace/cache and lookup-rids tests around 719-740; valid users, WORM, zero-data, volume serial, veto tests, and usershare tests in the fileserver loop; zero-readsize, share-list, ignore-domain, virus-scanner, and wide-link DFS tests later in the plan. The RPC list includes `rpc.samba3.spoolss`, `rpc.samba3.winreg`, `rpc.samba3.netlogon`, `rpc.svcctl`, `rpc.winreg`, and spoolss/netlogon variants that exercise the service-control code in this subset.

State and persistence: the script emits a plan to stdout; it does not run tests directly or mutate service state. Its "state" is derived from build configuration, platform, and helper-provided paths.

Dependencies and integration: central integration point for source3 testing. It maps scripts to environments such as `fileserver`, `simpleserver:local`, `ad_member:local`, `ad_member_idmap_nss:local`, `nt4_member:local`, and `clusteredmember:local`, and passes required environment variables into scripts as literal selftest substitutions.

Risks and test signals: because this file is plan-generation glue, regressions often appear as missing tests, tests run under the wrong environment, or wrong argument ordering. Feature guards such as `have_cluster_support` and `have_inotify` can silently suppress coverage. The best validation signal is a generated selftest plan containing the expected suite names and command arguments for each script.
