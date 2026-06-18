# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/accessors-fabrics.c

This generated C file provides public accessor functions for fabrics-related libnvme structures.

Accessor groups:
- `struct libnvmf_context`
  - Getters for connection strings: transport, traddr, host_traddr, host_iface, trsvcid, subsysnqn.
  - Setters/getters for queue size, IO/write/poll queue counts, reconnect delay, controller loss timeout, fast I/O fail timeout, keep-alive timeout, ToS.
  - Setters/getters for keyring ID, TLS key ID, configured TLS key ID.
  - Setters/getters for duplicate connect, disable SQ flow, header digest, data digest, TLS, and concat.
  - Setters/getters for default discovery retries and keep-alive timeout.
  - Getters for device, hostnqn, hostid, hostkey, ctrlkey, keyring, TLS key, and TLS key identity.
  - Setter/getter for persistent flag.

- `struct libnvmf_discovery_args`
  - Allocation/free helpers.
  - Default initializer sets max retries to 6 and LSP to `NVMF_LOG_DISC_LSP_NONE`.
  - Setters/getters for max retries and LSP.

- `struct libnvmf_uri`
  - Setters/getters for scheme, protocol, userinfo, host, port, path segments, query, and fragment.
  - String setters free existing values and duplicate new strings.
  - Path segment setter deep-copies a NULL-terminated string array and frees the old array.

Integration role:
- Public ABI layer for generated fabrics accessors.
- Used by C consumers and SWIG/Python binding support.
- Generated from internal structure definitions; comments identify Meson `update-accessors` as regeneration path.
