# Research: sources/user-network-fs/samba/source4/selftest/win/wintest_2k3_dc.sh

Purpose: executes smbtorture RPC groups against a Windows Server 2003 domain controller VM.

Important functions: `on_error()` increments `all_errs` and restores the DC snapshot. `drsuapi_tests()` runs DRSUAPI over `ncacn_ip_tcp` with `seal` and `seal,bigendian`. `spoolss_tests()` runs SPOOLSS over named pipes. `ncacn_ip_tcp_tests()` and `ncacn_np_tests()` iterate bind options over selected RPC suites.

Control flow and state: it sources the Windows config and shared functions, discovers the DC IP with `vm_get_ip.pl WIN2K3_DC_VM_CFG_PATH`, builds `OPTIONS` from DC credentials, dispatches on `TESTGROUP`, and exits with accumulated error count. Snapshot restore is the persistence recovery mechanism.

Dependencies and risks: depends on `bin/smbtorture`, VMware IP discovery, real network access, and Windows DC credentials. The bind options include a likely typo `ntml,seal` that may reduce intended NTLM coverage. Every failure restores the snapshot, which is safe but expensive.
