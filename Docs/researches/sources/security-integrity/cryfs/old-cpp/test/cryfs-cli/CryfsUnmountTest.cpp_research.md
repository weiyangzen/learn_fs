# sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/CryfsUnmountTest.cpp

Purpose: Tests the CryFS unmount CLI path by mounting a test filesystem and then unmounting it successfully.

Important APIs and types: Uses `CliTest`, `cryfs-cli/Cli.h`, `cryfs-unmount/Cli.h`, and helper `unmount`.

Control flow: The test creates/mounts a filesystem through the fixture, invokes the unmount CLI on the mount point, and asserts success.

State and persistence behavior: Uses real temporary mount/basedir state managed by the CLI fixture. The important persistent effect is the mount being removed.

Dependencies and integration points: Integrates main CryFS CLI mount behavior with the separate `cryfs-unmount` command.

Risks: Requires working mount/unmount support in the test environment. Cleanup failure can affect later tests.

Test signals: Mounted filesystem unmounts with success code and fixture teardown observes no lingering mount.
