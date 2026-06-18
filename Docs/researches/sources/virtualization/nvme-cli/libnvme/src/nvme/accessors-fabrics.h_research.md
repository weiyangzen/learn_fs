# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/accessors-fabrics.h

Auto-generated public declarations for NVMe-oF accessor functions over opaque internal structs: `libnvmf_context`, `libnvmf_discovery_args`, and `libnvmf_uri`.

Main API surface:
- `libnvmf_context_get_*` exposes borrowed strings for transport, target address, host address/interface, service ID, subsystem NQN, host identity, DH-CHAP/TLS/keyring strings, and device.
- `libnvmf_context_set/get_*` covers fabrics connection tunables: queue counts, queue size, reconnect policy, timeout policy, `tos`, key IDs, TLS booleans, digest booleans, duplicate connect, SQ flow disable, persistent, and defaults.
- `libnvmf_discovery_args_new/free/init_defaults` manages the opaque discovery argument object, with setters/getters for `max_retries` and log specific parameter `lsp`.
- `libnvmf_uri_set/get_*` exposes URI fields: scheme, protocol, userinfo, host, port, path segments, query, and fragment.

Dependencies and integration:
- Includes `<nvme/types.h>` and `<nvme/nvme-types.h>` for libnvme/NVMe scalar types such as `__u8`.
- The implementation is in the corresponding generated fabrics accessor source, not in this file.
- Used by higher-level discovery/connect code to keep the actual fabrics structs opaque to API consumers.

Ownership contract:
- Getter return values are borrowed and must not be freed by callers.
- URI string setters document copy-on-set semantics.
- `path_segments` is declared as a deep-copied NULL-terminated string array.

Risks and notes:
- This is generated code; manual edits are likely to be overwritten by `update-accessors`.
- The header intentionally exposes no validation policy. Callers can set invalid combinations; validation is performed later by fabrics connect/discovery code.
- ABI stability depends on keeping these declarations synchronized with generated implementations and the hidden internal struct fields.
