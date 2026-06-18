# Research: sources/user-network-fs/samba/source4/selftest/tests_win2k3_dc.sh

Purpose: registers Windows Server 2003 DC interoperability test groups with Samba selftest.

Control flow: it validates `WINTESTCONF`, sources `selftest/test_functions.sh`, exports `SRCDIR`, defines four groups (`RPC-DRSUAPI`, `RPC-SPOOLSS`, `ncacn_np`, `ncacn_ip_tcp`), and calls `testit $name rpc $SRCDIR/selftest/win/wintest_2k3_dc.sh $name` for each group.

State and dependencies: it depends on the shared selftest shell helper, `WINTESTCONF`, and `wintest_2k3_dc.sh` for the actual VM discovery and smbtorture execution. It does not persist local state; each child test may revert the DC snapshot on error.

Risks and test signals: the script assumes execution from a tree layout where `selftest/test_functions.sh` is resolvable. It provides a coarse group-level signal to selftest while detailed failures come from the child script.
