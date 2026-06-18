# Research: sources/user-network-fs/samba/source4/selftest/win/VMHost.pm

Purpose: Perl package wrapping VMware Server VMPerl and VIX APIs for Samba Windows selftests. It abstracts VM host connection, guest login, snapshot operations, file copy, command execution, and guest IP discovery.

Important APIs: `host_connect()` connects through VMPerl and VIX, powers on the guest via `start_guest()`, opens the VM, and logs into the guest OS. `host_disconnect()` and `host_reconnect()` reset handles. `create_snapshot()` creates a VIX snapshot and reconnects. `revert_snapshot()` powers off the guest, relying on VMware "Revert to Snapshot" behavior on power-on. `copy_to_guest()` creates a destination directory and copies either one file or flat directory contents using `copy_files_to_guest()`. `run_on_guest()` invokes `VMRunProgramInGuest()`. `get_guest_ip()` reads VMTools guest info key `ip`. `error()` returns and clears the package-level error state.

State and persistence: connection handles and credentials are package lexicals, so one process effectively manages one active VM context. Snapshot and power-state changes persist in VMware, while file copies and guest commands mutate the Windows guest. The destructor disconnects the host and releases handles.

Dependencies and integration: depends on `VMware::VmPerl`, `VMware::Vix::Simple`, and VMware Tools in the guest. It is used by `vm_get_ip.pl` and `vm_load_snapshot.pl`, and indirectly by Windows selftest shell scripts.

Risks and test signals: error state is global and reset on read, which can hide earlier failures if callers are careless. `revert_snapshot()` relies on external VM configuration instead of VIX snapshot selection. `copy_to_guest()` only copies flat directories and has weak path validation. Strong signals are successful host connection, nonempty guest IP, and clean VIX return codes.
