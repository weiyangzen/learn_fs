# File Research: sources/os/linux/linux/fs/smb/Kconfig

Top-level SMB filesystem Kconfig aggregator.

It sources client, server, and SMB Direct Kconfig files, then defines `SMBFS` as a tristate umbrella symbol selected by `CIFS` or `SMB_SERVER`. This lets common SMB code build when either client or server is enabled.

It also defines `SMB_KUNIT_TESTS`, gated by `SMBFS && KUNIT`, defaulting to `KUNIT_ALL_TESTS`, and documents that these tests are developer-only boot-time TAP-output tests.
