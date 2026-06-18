# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/private-fabrics.h

## Role

Internal NVMe-oF private header. It defines fabrics-layer context, hooks, discovery argument state, URI parsing state, extended attribute helpers, interface-address helpers, and controller matching declarations.

## Key Content

- Defines `struct libnvmf_hooks`, a callback table for:
  - retry decisions
  - successful connection notification
  - already-connected notification
  - discovery log handling
  - parser lifecycle and line iteration
- Defines `struct libnvmf_context`, which owns:
  - global libnvme context pointer
  - fabrics hooks
  - controller parameters
  - discovery retry/keep-alive defaults
  - persistent/device selection
  - host identity
  - authentication and TLS/keyring configuration
- Defines `struct libnvmf_discovery_args` with generated accessor/lifecycle annotations.
- Defines `struct libnvmf_uri` for parsed URI components: scheme, protocol, userinfo, host, port, path segments, query, and fragment.
- Provides inline helpers:
  - `libnvmf_exat_len()`
  - `libnvmf_exat_size()`
- Declares cached network interface access with `libnvmf_getifaddrs()` when network support is enabled.
- Defines `struct candidate_args` and `ctrl_match_t`, used by controller reuse/matching logic.
- Declares fabrics matching and entity helpers:
  - `libnvmf_ctrl_match_config()`
  - `libnvmf_ctrl_find()`
  - `libnvmf_get_entity_name()`
  - `libnvmf_get_entity_version()`

## Dependencies

- Includes `ifaddrs.h` when `NVME_HAVE_NETDB` or `CONFIG_FABRICS` is defined.
- Includes public `nvme/fabrics.h`, `nvme/tree.h`, and internal `nvme/private.h`.
- Uses `round_up()` from `private.h` for extended attribute sizing.

## Research Notes

This file separates fabrics-specific internals from the general private header so PCIe-only builds can omit fabrics accessors and code paths. The annotations such as `!generate-accessors` and `!access` indicate that code generation is part of the libnvme internal API maintenance process.

## Filesystem/Storage Relevance

This header supports discovery and connection to remote NVMe block devices. The matching helpers are important for avoiding duplicate fabric controller connections, which affects how remote storage appears in the OS topology.
