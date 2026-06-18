# Research: sources/user-network-fs/samba/source4/selftest/win/test_win.conf

Purpose: sample shell configuration for Windows selftests. It defines Perl library lookup, expect prompt behavior, Windows 2003 DC credentials/topology, smbtorture Windows host credentials, share paths, timeout, local Samba share settings, VMX paths, guest administrator credentials, and optional VMware host credentials.

State and dependencies: every value is exported into child shell, Perl, expect, and smbtorture processes. It bridges Samba selftest variables such as `NETBIOSNAME` to the Windows VM setup and binds tests to VMware inventory paths.

Integration points: consumed by `tests_win.sh`, `wintest_*` scripts, and the VM helper Perl scripts. The remote share path, backup hosts filename, drive letter, local hostname/IP, and credentials drive expect scripts not included in this item.

Risks and test signals: the file contains plaintext credentials and machine-specific VM paths, so it is suitable as local build-farm config rather than portable test data. Wrong host IP or VMX path causes setup failures before smbtorture can provide protocol signals.
