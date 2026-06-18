# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/tree-fabrics.c

## Role

Implements fabrics-specific topology matching and sysfs attribute harvesting for libnvme controller objects.

## Key Content

- Implements TCP controller matching when kernels do not expose `src_addr`:
  - `_tcp_ctrl_match_host_traddr_no_src_addr()`
  - `_tcp_ctrl_match_host_iface_no_src_addr()`
  - `_tcp_opt_params_match_no_src_addr()`
- Implements TCP controller matching when `src_addr` is available:
  - `_tcp_opt_params_match()`
  - `_tcp_match_ctrl()`
- Implements generic non-TCP matching:
  - `_libnvmf_tree_ctrl_match()`
- Initializes candidate matching state:
  - `libnvmf_candidate_init()`
  - `_libnvmf_candidate_init()`
- Reads fabrics security attributes from sysfs:
  - `libnvmf_read_sysfs_dhchap()`
  - `libnvmf_read_sysfs_tls()`
  - `libnvmf_read_sysfs_tls_mode()`
  - `libnvmf_read_sysfs_fabrics_attrs()`
- Public/internal lookup helpers:
  - `libnvme_ctrl_find()`
  - `libnvmf_ctrl_match_config()`
  - `libnvmf_ctrl_find()`

## Behavior

- TCP matching requires transport, `trsvcid`, destination `traddr`, discovery-controller state where relevant, and subsystem NQN where relevant.
- `host_traddr` and `host_iface` are optional TCP inputs. If a caller specifies either, the code tries to verify them.
- On kernels with `src_addr` in the controller `address` sysfs attribute, matching can infer source address and interface more accurately.
- On older kernels without `src_addr`, matching is intentionally optimistic when not enough data exists.
- Discovery controller matching handles the well-known discovery NQN specially: a controller connected with the well-known NQN may later expose a unique NQN, so the candidate records `well_known_nqn` and ignores direct NQN comparison.
- TLS sysfs values are parsed from hex string IDs into `cfg.tls_key_id` and `cfg.tls_configured_key_id`.

## Dependencies

- Includes networking, libnvme public headers, cleanup helpers, `private.h`, and `private-fabrics.h`.
- Uses helpers declared in `private.h`, including `streq0()`, `streqcase0()`, `libnvme_ipaddrs_eq()`, `libnvme_iface_matching_addr()`, and `libnvme_iface_primary_addr_matches()`.

## Research Notes

The core purpose is avoiding duplicate controller objects/connections while accounting for differences in kernel sysfs reporting across versions. The optimistic fallback on older kernels is explicitly documented as not perfectly accurate.

## Filesystem/Storage Relevance

Controller matching influences whether NVMe-oF paths/controllers are reused or duplicated in user-space topology. This affects how remote block devices are discovered, managed, and represented to higher-level storage tooling.
