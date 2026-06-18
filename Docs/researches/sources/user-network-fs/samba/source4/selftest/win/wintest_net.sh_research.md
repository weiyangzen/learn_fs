# Research: sources/user-network-fs/samba/source4/selftest/win/wintest_net.sh

Purpose: runs NET-API smbtorture suites against a Windows server over selected DCE/RPC transports.

Control flow: after sourcing configuration and validating credentials, it defines test lists for `ncalrpc`, `ncacn_np`, and `ncacn_ip_tcp`, loops over bind options `seal,padcheck` and `bigendian`, selects the right test list by transport, and invokes `$SMBTORTURE_BIN_PATH -U user%password -W domain transport:server[opts] TEST`.

State and dependencies: no local persistent state; failures call `restore_snapshot` on the configured VM. Depends on smbtorture, real network access, and Windows credentials.

Risks and test signals: failing tests are documented in comments and excluded from lists, so this is a regression suite for known-working NET-API paths. Snapshot restore on every failure can mask independent failures but preserves VM cleanliness.
