<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/virtiofs/fs_test.go -->
# sources/user-network-fs/go-fuse/virtiofs/fs_test.go

## Purpose
Runs a basic end-to-end virtiofs QEMU test against a host loopback filesystem served by go-fuse.

## Important APIs, Types, and Functions
`killNotifyRoot`, its `Lookup`, and `TestBasic` are the main pieces.

## Control Flow
The test creates host files, starts `ServeFS` on a vhost-user socket, builds an initrd with a script, boots QEMU with `vhost-user-fs-pci`, mounts virtiofs in the guest, copies and lists files, then signals completion by looking up `killme.txt`.

## State and Persistence Behavior
State includes temp host directory, socket, initrd, QEMU process, and condition-variable flags for guest progress.

## Dependencies and Integration Points
Depends on `fs.LoopbackNode`, `mkinitRam`, prepared kernel/busybox/modules, QEMU/KVM, and the internal vhost-user backend.

## Risks and Edge Cases
Environment requirements are heavy; QEMU is killed externally because guest poweroff was unreliable. Test can hang if sentinel lookup never happens.

## Test Signals
The test verifies copied file contents and directory listing written back through virtiofs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/virtiofs/fs_test.go -->
