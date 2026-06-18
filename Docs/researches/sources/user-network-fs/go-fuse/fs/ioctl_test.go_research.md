# sources/user-network-fs/go-fuse/fs/ioctl_test.go

Purpose: tests FUSE ioctl dispatch into a node implementation.

Important types/functions: `ioctlNode.Ioctl` copies input bytes plus one into output and returns result code `1515`; `TestIoctl` opens the mounted root, builds a read/write ioctl command with internal `ioctl.New`, calls raw `SYS_IOCTL` with a byte buffer, and verifies result and transformed buffer.

State/dependencies: real FUSE mount, unsafe pointer to buffer, ioctl command encoding.

Risks/test signals: covers input/output buffer wiring and result propagation. It is Linux/Unix syscall-sensitive and assumes non-empty buffers for unsafe pointer use.
