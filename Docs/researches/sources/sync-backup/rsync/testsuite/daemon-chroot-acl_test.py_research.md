# sources/sync-backup/rsync/testsuite/daemon-chroot-acl_test.py

Purpose: regression for hostname-based daemon `hosts deny` matching when `daemon chroot` is enabled and reverse DNS resources may be absent inside the chroot.

Important APIs/types/functions: `require_tcp`, `_can_chroot`, optional `unshare --user --map-root-user` re-exec, `_client_hostname`, `write_conf`, `run_check`, `start_test_daemon`, and `test_xfail`/skip/fail helpers.

Control flow: require Linux TCP and chroot capability. Determine reverse hostname for 127.0.0.1, create a chroot with module root, start daemon once, then rewrite config between two scenarios: global reverse lookup and per-module reverse lookup only. In both cases, a pull should be denied with `@ERROR access denied`.

State and persistence behavior: daemon chroot directory contains module data; config file is rewritten per connection because rsyncd rereads it. Log output is printed for diagnosis.

Dependencies and integration points: real TCP peer address, chroot, NSS/reverse DNS behavior, daemon ACL evaluation, and module/global `reverse lookup`.

Risks and test signals: platform and privilege heavy, so many skips are legitimate. Failure means hostname deny was bypassed after chroot, matching the security advisory scenario.
