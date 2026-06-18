# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/fabrics.h

Public header for NVMe-over-Fabrics definitions and APIs.

Exports:
- Default controller loss timeout `NVMF_DEF_CTRL_LOSS_TMO`.
- Opaque `struct libnvmf_context`, `struct libnvmf_discovery_args`, and `struct libnvmf_uri`.
- Enum-to-string helpers for discovery log transport/address/subtype/TREQ/EFLAGS/SECTYPE/RDMA fields.
- Controller connect/disconnect APIs: `libnvmf_add_ctrl`, `libnvmf_connect_ctrl`, `libnvmf_connect`, `libnvmf_connect_config_json`, `libnvmf_disconnect_ctrl`.
- Discovery APIs: `libnvmf_get_discovery_log`, `libnvmf_discovery`, `libnvmf_discovery_config_json`, `libnvmf_discovery_config_file`, `libnvmf_discovery_nbft`.
- Registration API: `libnvmf_is_registration_supported`, `libnvmf_register_ctrl`.
- URI API: `libnvmf_uri_parse`, `libnvmf_uri_free`.
- Context creation, hook installation, connection/host/crypto/device/queue/reconnect setters.
- NBFT read/free APIs.

Integration:
- Includes `<nvme/tree.h>` for topology types like `libnvme_ctrl_t` and `libnvme_host_t`.
- Implemented by `fabrics.c` and accessor-generated files.
- Consumers use this API to perform connect-all, discovery, persistent discovery controller handling, and boot-table discovery without private struct access.

Contract notes:
- Hooks provide retry, connected, already-connected, discovery-log, and parser callbacks.
- `libnvmf_get_default_trsvcid()` returns constant default service strings, despite documentation saying allocated string.
- Context setters return errno-style status but often only assign fields.

Risks:
- Documentation has minor typos and a few ownership inaccuracies.
- Because context internals are opaque, accessors must remain synchronized with this header for users needing fine-grained field control.
