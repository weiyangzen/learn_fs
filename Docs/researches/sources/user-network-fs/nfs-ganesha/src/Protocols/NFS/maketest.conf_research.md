## sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/maketest.conf

Purpose: defines a mount protocol test harness rule.

APIs and flow: `Test mount_protocol` runs architecture-specific `test_mntproto`, expects stdout markers for `test_mnt_Null : OK` and `test_mnt_Export : OK`, and defines failure classifications for missing markers, generic `ERROR`, and nonzero exit status.

State/dependencies: external test runner configuration only; depends on command path conventions and stdout strings emitted by the mount protocol test binary.

Risks/tests: brittle string matching can miss changed test output or overmatch unrelated `ERROR`. Use it as a signal that MOUNT null/export basics still work, not as coverage for `mnt_Mnt` access and auth-flavor behavior.
