# sources/test-tools/syzkaller/vm/gvisor/gvisor.go

## Purpose

`gvisor.go` implements a VM backend for testing gVisor/runsc as the target kernel-like environment. It creates an OCI bundle, launches a runsc sandbox, copies test binaries into the root, executes commands inside the sandbox, and exposes a stdin-based proxy path for manager connections.

## Important APIs, Types, and Functions

Key types are `Config`, `Pool`, and `instance`; the backend registers under `targets.GVisor`. Important functions include `ctor`, `Pool.Count`, `Pool.Create`, `waitBoot`, `args`, `Info`, `runscCmd`, `Close`, `Forward`, `Copy`, `Run`, `guestProxy`, `Diagnose`, the proxy `init`, and constants/templates `initStartMsg`, `configTempl`, and `sandboxCaps`.

## Control Flow

`Create` builds root/image/bundle directories, writes `config.json`, copies the current binary as `/init`, creates a panic FIFO, starts `runsc run`, and waits for `SYZKALLER INIT STARTED` from the init path. `Run` builds `runsc exec` with root capabilities, wires stdout/stderr into the merger, optionally passes a Unix socketpair endpoint as stdin for manager proxying, starts the command, and kills the sandbox command on context timeout. `guestProxy` bridges the host TCP manager port to a Unix socket passed into the guest.

## State and Persistence Behavior

Instance state tracks the runsc root, image directory, sandbox name, command process, output merger, and one forwarded port. It writes bundle config and copied binaries under workdir, creates a FIFO, and manages a runsc container name in the runsc root. `Close` deletes the container forcefully and waits for merger/process cleanup.

## Dependencies and Integration Points

It depends on a runsc binary supplied as `env.Image`, OCI runtime config semantics, cgroup resource fields, Linux FIFOs/socketpairs, `vmimpl` output merging, and syzkaller's host-fuzzer forwarding expectations.

## Risks and Test Signals

Command splitting uses whitespace and cannot preserve complex shell quoting. `Close` assumes `inst.cmd` exists after successful create. Memory/cpu limit validation must match host resources. Integration tests should cover boot success/failure messages, panic-log capture, copy permissions, single-forward enforcement, proxy data flow, timeout killing, and diagnosis stack/dmesg collection.
