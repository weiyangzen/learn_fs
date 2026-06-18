<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/test_w2k3.sh -->
# sources/user-network-fs/samba/source4/selftest/test_w2k3.sh

Purpose: runs a curated set of RPC torture tests expected to pass against a Windows Server 2003 DC.

Important APIs/types/functions: `test_functions.sh`, `testit`, `smbtorture`, transport lists for `ncacn_np` and `ncacn_ip_tcp`, bind options such as `padcheck`, `sign`, `seal`, `bigendian`, and RPC test names.

Control flow: validates server, username, password, domain, and realm arguments, builds authentication options, runs a spoolss named-pipe test, then loops bind options, transports, and RPC test lists, finally running DRSUAPI over sealed TCP in normal and big-endian modes.

State and persistence behavior: remote RPC tests may create temporary server state depending on smbtorture subtests; the script itself writes no files.

Dependencies and integration points: used for interoperability testing against a real W2K3 DC with administrator credentials.

Risks: requires live Windows infrastructure and credentials. Some smbtorture tests may be invasive. Argument shift expects five values after only checking at least four, so missing realm can behave poorly.

Test signals: `testit` subunit results for each RPC/transport/bind-option combination.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/test_w2k3.sh -->
