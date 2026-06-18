# File Research: sources/virtualization/nvme-cli/libnvme/test/tree.c

This file is a focused unit test for non-fabrics libnvme tree operations: host lookup/deduplication, subsystem lookup/deduplication, getters, and iteration macros.

Test cases:
- `test_host_dedup()` confirms `libnvme_lookup_host(ctx, hostnqn, hostid)` returns the same pointer for identical host credentials and a different pointer for different credentials.
- `test_hostid_from_hostnqn()` verifies that passing NULL `hostid` derives the host UUID from an NQN of the form `nqn.2014-08.org.nvmexpress:uuid:<uuid>`.
- `test_host_attrs()` validates `libnvme_host_get_hostnqn()` and `libnvme_host_get_hostid()`.
- `test_host_iteration()` creates three hosts and verifies `libnvme_for_each_host()` visits exactly three.
- `test_subsystem_dedup()` checks `libnvme_lookup_subsystem()` pointer reuse for identical name/NQN and distinct objects for different subsystem identities.
- `test_subsystem_attrs()` validates `libnvme_subsystem_get_name()` and `libnvme_subsystem_get_subsysnqn()`.
- `test_subsystem_iteration()` verifies `libnvme_for_each_subsystem()` count.

Integration:
- Uses `libnvme_create_global_ctx(stdout, LIBNVME_LOG_ERR)` and frees it after each test.
- Includes `<nvme/private.h>` to access tree-related types/macros.
- Meson builds it as `test-tree` and registers `libnvme - tree`.

Risk and maintenance notes:
- The tests assert allocation success, so they abort rather than report graceful failure on setup errors.
- Coverage is intentionally in-memory; it does not scan `/sys` or require hardware.
