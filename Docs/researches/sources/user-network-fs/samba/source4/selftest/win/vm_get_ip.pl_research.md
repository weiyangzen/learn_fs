# Research: sources/user-network-fs/samba/source4/selftest/win/vm_get_ip.pl

Purpose: command-line Perl helper that connects to a VMware VM and prints the guest IP address.

Control flow: it reads the VMX path from the environment variable named by `ARGV[0]`, reads optional host connection parameters and guest administrator credentials, creates a `VMHost` object, calls `host_connect()`, then `get_guest_ip()`, printing the result.

State and dependencies: depends on `PERLLIB` or `-I` pointing to `VMHost.pm`, VMware host connectivity, guest credentials, and VMware Tools reporting the IP. It mutates VM power state because `host_connect()` powers on a stopped guest.

Risks and test signals: missing or empty environment variables produce VMware connection errors rather than local validation errors. A nonempty printed IP is the main signal consumed by `wintest_2k3_dc.sh`.
