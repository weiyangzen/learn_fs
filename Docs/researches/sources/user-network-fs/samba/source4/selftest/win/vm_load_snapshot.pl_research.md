# Research: sources/user-network-fs/samba/source4/selftest/win/vm_load_snapshot.pl

Purpose: Perl helper to connect to the configured VMware VM and revert it to its snapshot state.

Control flow: it reads `VM_CFG_PATH`, host connection variables, and guest admin credentials, connects via `VMHost->host_connect()`, then calls `revert_snapshot()`. `check_error()` terminates with a diagnostic if either operation records an error in `VMHost`.

State and dependencies: it changes persistent VM state by powering off and reconnecting to trigger snapshot restoration. It relies on the same VMware APIs and guest credentials as `vm_get_ip.pl`.

Risks and test signals: it performs a full VM connection before reverting, which can fail if the guest is already unhealthy. The test signal is process exit code; no subunit formatting is emitted.
