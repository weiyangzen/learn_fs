## sources/user-network-fs/go-fuse/fuse/mount_linux_test.go

Purpose: Linux integration tests for mount option handling, direct mount behavior, inherited `/dev/fd/N`, suid/dev flags, and max-write negotiation.

Important APIs/types/functions: `TestMountDevFd`, `TestMountMaxWrite`, `mountCheckOptions`, `TestDirectMount`, `TestDirectMountDevSuid`, and `TestEscapedMountOption`.

Control flow: tests mount small raw filesystems under different `MountOptions`, inspect mountinfo and syscall stat results, verify helper/direct flags, and unmount cleanly.

State and persistence: temporary mountpoints and kernel mount table entries are created for each test.

Dependencies and integration: uses Linux mountinfo parsing, raw FUSE mount code, and environment privileges.

Risks and test signals: tests are environment-sensitive but critical for preventing regressions in option escaping, mount security flags, and max request sizes.
