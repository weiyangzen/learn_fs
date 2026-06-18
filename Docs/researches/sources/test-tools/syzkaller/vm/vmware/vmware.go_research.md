# sources/test-tools/syzkaller/vm/vmware/vmware.go

Purpose: VMware-backed syzkaller VM implementation using `vmrun` clone/start/IP discovery, SSH command execution, and a serial Unix socket for kernel output.

Important APIs/types/functions: `Config` (`base_vmx`, `count`), `Pool`, `instance`, `ctor`, `Pool.Create`, `clone`, `boot`, `Forward`, `Close`, `Copy`, `Run`, and `Diagnose`.

Control flow: `ctor` parses config and validates `vmrun`. `Create` creates a timestamped VMX path in the workdir, clones the base VMX, and boots it. `boot` starts the VM nogui, waits for guest IP via `vmrun getGuestIPAddress -wait`, and stores it. `Run` dials a `serial` Unix socket beside the VMX, creates SSH stdout/stderr pipes, builds SSH args with optional reverse forwarding, starts `ssh`, adds dmesg/stdout/stderr to a new `OutputMerger`, and uses `vmimpl.Multiplex`.

State and persistence: a full VMware clone is created under the workdir and deleted by `vmrun deleteVM` on `Close`. Runtime state includes guest IP, close channel, optional forward port, and command-local merger.

Dependencies and integration: depends on `vmrun`, host SSH/SCP, a serial socket created/configured by the VMX, `vmimpl` SSH/SCP and Multiplex helpers.

Risks: no `WaitForSSH` after IP discovery; serial socket absence fails each run; cleanup ignores `vmrun` errors; `Diagnose` is empty; timestamp path avoids most collisions but relies on full clone cost.

Test signals: no direct test assigned. Integration tests must validate clone, boot, IP discovery, serial socket, SSH, SCP, run, and cleanup.
