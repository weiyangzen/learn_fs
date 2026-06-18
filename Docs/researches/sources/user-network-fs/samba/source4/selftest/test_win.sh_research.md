<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/test_win.sh -->
# sources/user-network-fs/samba/source4/selftest/test_win.sh

Purpose: orchestrates Windows 2003 VM interoperability tests through the `wintest` harness.

Important APIs/types/functions: `selftest/test_functions.sh`, `vm_get_ip.pl`, `restore_snapshot`, `testit`, `wintest_base.sh`, `wintest_raw.sh`, `wintest_rpc.sh`, `wintest_net.sh`, `wintest_client.sh`, and `wintest_2k3_dc.sh`.

Control flow: obtains the remote Windows VM IP from `VM_CFG_PATH`, restores the snapshot and exits if missing, then runs BASE, RAW, RPC, NET, Windows-client-against-Samba, and selected DC RPC tests with environment-provided credentials.

State and persistence behavior: external VM tests may mutate the Windows guest and Samba test environment; snapshot restore handles the initial IP failure path only.

Dependencies and integration points: requires `WINTEST_DIR`, VM configuration, credentials/workgroup environment variables, and the wintest scripts.

Risks: highly environment-specific and dependent on a working VM controller. Failure paths outside initial IP discovery do not automatically restore snapshots in this wrapper.

Test signals: `testit` subunit results for each wintest phase.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/test_win.sh -->
