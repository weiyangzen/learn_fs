## sources/security-integrity/libcap/go/try-launching.go

Purpose: validates Go `cap.Launcher` behavior for normal launches, UID/GID/group changes, IAB setup, chroot, and capability modes.

Important APIs/functions: `cap.NewLauncher`, `Launcher.Callback`, `SetChroot`, `SetUID`, `SetGroups`, `SetMode`, `SetIAB`, `Launch`, `cap.IABFromText`, `cap.GetBound`, and `syscall.Wait4`.

Control flow: determines the libcap tree root and whether `CAP_SYS_ADMIN` is bounded, builds a table of launch scenarios with expected failures based on privilege, configures each launcher, starts all possible children, and waits for exit status validation.

State/persistence: creates child processes with changed credentials/modes/chroot/IAB; parent tracks PIDs/statuses only.

Dependencies/integration: Go cap package, built `go/ok`, `progs/tcapsh-static`, kernel chroot/user/capability support, root privilege for full coverage. Run in `go/Makefile` `sudotest`.

Risks: root/path inference uses the current working directory; expected-failure logic depends on current uid and bounding set; skipped failures can hide unsupported features.

Test signals: `./try-launching` and `sudo ./try-launching`, plus cgo variant when required.
