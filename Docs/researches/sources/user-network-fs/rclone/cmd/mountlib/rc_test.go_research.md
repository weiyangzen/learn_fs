# sources/user-network-fs/rclone/cmd/mountlib/rc_test.go

Purpose: integration-tests RC mount endpoints with a local backend.

Important flow: imports local, cmount, mount, and mount2 for registration; installs config; retrieves RC calls; creates a local source with `file.txt`; calls `mount/types`; checks error cases; mounts local source; stats file through mountpoint; checks `mount/listmounts`; unmounts and verifies empty list.

State/persistence: uses temp directories and real OS mountpoints; may remove mountpoint on Windows. It sleeps briefly before unmount to avoid OS immediate-use races.

Dependencies/integration: `rc.Calls`, `configfile.Install`, platform runtime, testify, and `testy.SkipUnreliable` on Darwin. Risks are environmental: missing FUSE privileges, CI hangs, OS timing. Test signal is high-value for RC lifecycle but conditional.
