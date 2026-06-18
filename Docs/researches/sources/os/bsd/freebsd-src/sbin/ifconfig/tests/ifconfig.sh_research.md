# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/tests/ifconfig.sh

`ifconfig.sh` is an ATF shell test file for general ifconfig behavior. It sources the shared VNET test helper from `../../sys/common/vnet.subr`.

The only test case is `badfib`. It requires root, initializes VNET state, creates an epair, verifies assigning FIB 0 succeeds, then verifies assigning FIB `net.fibs` fails with non-empty stderr because that FIB is outside the configured range.

Cleanup calls `vnet_cleanup`. `atf_init_test_cases()` registers `badfib`.

The test exercises argument validation and kernel error handling for per-interface FIB assignment in an isolated VNET environment.
