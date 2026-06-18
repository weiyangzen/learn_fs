# File Research: sources/virtualization/nvme-cli/libnvme/test/tree-fabrics.c

This file is a libnvme unit test for NVMe-oF/transport-aware tree controller lookup and matching behavior. It constructs in-memory `libnvme_global_ctx` trees with hosts, subsystems, and controllers, then validates that controller identity matching behaves correctly for TCP, RDMA, FC, PCIe, loop, discovery controllers, source-address extraction, and paginated lookup.

Key structures and helpers:
- `struct test_data` holds input `libnvmf_context`, subsystem name, expected subsystem/controller pointers, and a generated controller id.
- `DEFAULTS(...)` seeds fabric controller params for TCP/RDMA/FC test cases.
- `create_tree()` builds one host/subsystem and creates controllers from `test_data` using `libnvme_get_subsystem()` and `libnvme_lookup_ctrl()`.
- `show_ctrl()` and `match_ctrl()` print and validate controller attributes through getters such as `libnvme_ctrl_get_transport()`, `libnvme_ctrl_get_traddr()`, `libnvme_ctrl_get_host_traddr()`, and `libnvme_ctrl_get_trsvcid()`.
- `ctrl_match()` is the central table-test helper: it creates a reference controller, optionally fakes sysfs-style `name` and `address`, calls `libnvmf_ctrl_find()` before `libnvme_lookup_ctrl()`, and checks whether candidate params should match or create a distinct controller.
- `ctrl_config_match()` separately tests `libnvmf_ctrl_match_config()` against a reference controller.

Major test coverage:
- `test_lookup()` verifies controller creation, tree count, deduplication, and lookup relaxation rules. TCP lookups test combinations of `trsvcid`, `host_traddr`, and `host_iface`; non-TCP default lookup clears host interface and service id.
- `test_src_addr()` directly mutates private `c->address` strings and checks `libnvme_ctrl_get_src_addr()` for NULL/empty input, missing `src_addr`, IPv4, IPv6, and IPv6 zone/scope suffix stripping.
- `test_ctrl_match_fc()` validates FC matching by transport, traddr, trsvcid, and host_traddr, with relaxed matching when candidate host binding is absent.
- `test_ctrl_match_rdma()` mirrors FC-style cases for RDMA, using IP address equality for traddr/host_traddr.
- `test_ctrl_match_tcp()` is the largest matrix. It validates IPv4 and IPv6 TCP candidate/reference matching against mocked interfaces:
  - `eth0`: `192.168.1.20`, `fe80::dead:beef`
  - `lo`: `127.0.0.1`, `::1`
  It tests unspecified source binding, explicit `host_traddr`, explicit `host_iface`, matching/non-matching local addresses, loopback behavior, and sysfs `address` strings with `src_addr=...`.
- `test_ctrl_config_match()` checks config-level matching for TCP, including subsystem NQN behavior.
- `test_ctrl_match_pcie()` verifies PCIe matching by transport and case-insensitive BDF-style `traddr`; NULL candidate `traddr` is treated as a match.
- `test_ctrl_match_loop()` verifies loop transport matching by transport alone.
- `test_well_known_nqn()` checks `NVME_DISC_SUBSYS_NAME`: candidates for the well-known discovery NQN only match controllers marked with `libnvme_ctrl_set_discovery_ctrl(..., true)`.
- `test_none_normalization()` validates that `"none"` for `host_traddr` or `host_iface` behaves like NULL.
- `test_ctrl_config_match_rdma()` and `test_ctrl_config_match_fc()` validate `libnvmf_ctrl_match_config()` for those transports.
- `test_lookup_ctrl_pagination()` checks the `p` argument to `libnvme_lookup_ctrl()`: searches begin after `p`, so earlier matches are skipped and later duplicate candidates can be created/found.

Dependencies and integration:
- Includes public libnvme and private headers: `<libnvme.h>`, `<nvme/private.h>`, `<nvme/private-fabrics.h>`.
- Relies on private struct access (`c->address`, `reference_ctrl->name`) for test setup.
- Meson wires it as `libnvme - tree-fabrics` only when the mocked ifaddrs support is available, using `mock-ifaddrs.c`/environment per `libnvme/test/meson.build`.

Risk and maintenance notes:
- The test intentionally assigns string literals to private `reference_ctrl->address` and resets fields to NULL before freeing to avoid freeing non-owned memory. Future ownership changes in controller internals could make this brittle.
- The table matrix encodes subtle matching policy. Any change to `_candidate_init*`, `libnvmf_ctrl_find()`, interface probing, source address normalization, or `libnvmf_ctrl_match_config()` should update expected cases here.
- Error paths in `ctrl_match()` return before `libnvme_free_global_ctx()` in several failure branches, acceptable for a short-lived failing test but still a leak under failure diagnostics.
