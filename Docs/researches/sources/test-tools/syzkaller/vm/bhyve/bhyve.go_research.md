# sources/test-tools/syzkaller/vm/bhyve/bhyve.go

## Purpose

`bhyve.go` implements a FreeBSD bhyve VM backend. It creates per-instance disk clones or copies, sets up networking, boots VMs, waits for SSH, and runs commands with merged console and SSH output.

## Important APIs, Types, and Functions

Key types are `Config`, `Pool`, and `instance`; the backend registers as `bhyve` with overcommit. Important functions are `ctor`, `Pool.Count`, `Pool.Create`, `Boot`, `Close`, `Forward`, `Copy`, `Run`, `Diagnose`, and `parseIP`.

## Control Flow

`Create` prepares an instance name and SSH options, creates a ZFS snapshot/clone when `Dataset` is configured or copies the image into workdir otherwise, optionally creates and bridges a tap device, then calls `Boot`. `Boot` destroys any old VM, selects tap or slirp networking, optionally runs `bhyveload`, starts `bhyve`, captures console output, waits for an IP in DHCP output or uses localhost for slirp, and waits for SSH. `Run` starts an SSH command with optional port forwarding and adds its streams to the existing console merger.

## State and Persistence Behavior

Instance state tracks image copy/clone path, ZFS snapshot, tap device, forward port, bhyve process, console writer, and output merger. It mutates host state through ZFS snapshots/clones, copied images, tap interfaces, bridge membership, bhyve VMs, and SSH/SCP transfers. `Close` kills the VM and cleans these resources best-effort.

## Dependencies and Integration Points

It depends on FreeBSD host tooling (`bhyve`, `bhyveload`, `bhyvectl`, `ifconfig`, optional `zfs`), SSH helpers, and `vmimpl` multiplex/diagnose helpers. It implements the syzkaller VM instance interface.

## Risks and Test Signals

Boot success depends on DHCP/IP log parsing, host network setup, ZFS layout, image compatibility, and bhyve process cleanup. `Forward` supports only one slirp forward. Unit coverage is absent here, so useful tests are integration boot/SSH/copy/run/diagnose cycles, ZFS cleanup failure handling, tap bridge cleanup, and `parseIP` samples.
