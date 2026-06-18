# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/tests/basic.sh

Purpose: ATF sanity tests for core `nvmecontrol` behavior.

Key behavior:
- Selects the first `/dev/nvmeN` controller, defaulting to `nvme0` if none exists.
- Defines `DANGEROUS=false` to skip real reset testing by default.
- Tests module-load error handling by creating fake `.so` files under `/lib/nvmecontrol` and `/usr/local/lib/nvmecontrol` when directories exist.
- Smoke-tests `admin-passthru`, `devlist`, `identify`, `io-passthru`, `logpage`, `nsid`, `power`, and `reset`.
- For each command, checks behavior both when an NVMe character device exists and when it does not.
- Verifies invalid option `-z` produces the expected parser error.

Dependencies:
- FreeBSD ATF shell framework.
- Root privileges for all tests.
- Installed `nvmecontrol`.

Research notes:
- This is explicitly a basic sanity test, not exhaustive functional coverage.
- Reset of an active device is skipped unless `DANGEROUS=true`.
