# sources/user-network-fs/nfs-utils/tests/test-lib.sh

Purpose: `test-lib.sh` is shared shell infrastructure for nfs-utils tests.

Important APIs and control flow: It resolves and validates `srcdir`, extends `PATH` with the test and `nsm_client` directories, and provides environment checks such as `check_root` and `check_dev_log`. It also supplies common setup/cleanup helpers used by statd tests.

State, dependencies, and integration: It exports PATH changes and interacts with root privileges, `/dev/log`, and temporary test directories. Test scripts source it before invoking helper binaries.

Risks and test signals: Hard environment requirements can make tests fragile in containers or unprivileged CI. Tests should verify skip/fail behavior is explicit, cleanup runs on failure, and build-tree versus source-tree paths work.
