# sources/test-tools/syzkaller/vm/vmm/vmm.go

Purpose: OpenBSD `vmm`/`vmctl` backend for syzkaller, using OpenBSD virtualization to boot kernel/image pairs and run commands over SSH.

Important APIs/types/functions: `Config`, `Pool`, `instance`, `ctor`, `Pool.Create`, `Boot`, `lookupSSHAddress`, `Close`, `Forward`, `Copy`, `Run`, `Diagnose`, `vmctl`, and `vmctlStatusRegex`.

Control flow: `ctor` validates image, kernel, count, and memory config. `Create` prepares an instance disk with `vmctl create`, stops stale VMs by name, then calls `Boot`. `Boot` starts `vmctl start` with kernel, disk, local network, and console connection, adds console output to a merger, derives SSH address from `vmctl status` VM id as `100.64.<id>.3`, and waits for SSH. `Run` adds SSH stdout/stderr to the same merger and starts `ssh`; a custom goroutine handles context timeout or merger errors. `Diagnose` sends OpenBSD DDB commands.

State and persistence: creates a per-instance qcow2 image in the workdir, runs a `vmctl` process, and holds a console writer. `Close` stops the VM, closes console input, kills/waits the process, and waits for merger shutdown.

Dependencies and integration: depends on OpenBSD `vmctl`, SSH/SCP, syzkaller `vmimpl` helpers, and OpenBSD DDB diagnosis.

Risks: address derivation depends on `vmctl status` formatting and network convention; boot failure reads only one output chunk; stale stop is racy by comment; `Run` uses custom lifecycle rather than `Multiplex`; `Forward` assumes guest host-side address `.2`.

Test signals: no direct unit test. Integration requires OpenBSD host `vmm`, kernel/image artifacts, SSH, and console behavior.
