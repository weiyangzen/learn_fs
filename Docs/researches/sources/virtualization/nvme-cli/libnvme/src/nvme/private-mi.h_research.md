# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/private-mi.h

## Role

Internal NVMe Management Interface header. It defines MI request/response containers, endpoint state, transport operations, AEM state, MCTP test injection hooks, and MI transport-handle bridge declarations.

## Key Content

Under `CONFIG_MI`, defines:

- `struct libnvme_mi_req` and `struct libnvme_mi_resp`, wrapping MI headers, payload pointers, lengths, and MIC values.
- `struct libnvme_mi_aem_ctx`, holding asynchronous event occurrence list traversal state and callbacks.
- `struct libnvme_mi_ep`, representing an MI endpoint:
  - global context
  - transport driver
  - transport-private data
  - controller list
  - timeout/MPRT/quirk state
  - command set identifier
  - inter-command delay tracking
  - AEM state
  - submit tracing callbacks
- `struct libnvme_mi_transport`, the internal transport vtable:
  - `submit`
  - `close`
  - endpoint description
  - timeout check
  - AEM file descriptor/read/purge operations
- MI endpoint helpers:
  - `libnvme_mi_init_ep()`
  - `libnvme_mi_ep_probe()`
  - `libnvme_mi_crc32_update()`
- MCTP socket mock operations for tests through `struct __mi_mctp_socket_ops` and `__libnvme_mi_mctp_set_ops()`.
- MI quirk flags:
  - `LIBNVME_QUIRK_MIN_INTER_COMMAND_TIME`
  - `LIBNVME_QUIRK_CSI_1_NOT_SUPPORTED`

Outside `CONFIG_MI`, it still declares transport-handle bridge functions:

- `__libnvme_transport_handle_open_mi()`
- `__libnvme_transport_handle_init_mi()`
- `__libnvme_transport_handle_close_mi()`

## Dependencies

- Conditional on `CONFIG_MI` for most definitions.
- Includes polling, socket, list, and public `nvme/mi.h` APIs.
- Uses CCAN intrusive lists.

## Research Notes

This header forms the internal boundary between generic libnvme transport handles and MI transports. The MCTP socket ops are intentionally private and test-oriented, allowing tests to replace socket operations without exposing the hook in the shared library ABI.

## Filesystem/Storage Relevance

MI is management-plane rather than data-plane. It supports storage inventory, health, and event processing for NVMe devices that may expose block namespaces.
