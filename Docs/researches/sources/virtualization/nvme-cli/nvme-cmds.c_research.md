# File Research: sources/virtualization/nvme-cli/nvme-cmds.c

This file provides small nvme-cli command helper wrappers for namespace attachment and detachment.

Core helper:
- `nvme_ns_attachment(struct libnvme_transport_handle *hdl, bool ish, __u32 nsid, __u16 num_ctrls, __u16 *ctrlist, bool attach)`
  - Creates `struct nvme_ctrl_list cntlist`.
  - Initializes it with `nvme_init_ctrl_list()`.
  - If `ish` and the handle is an MI handle, calls `nvme_init_mi_cmd_flags(&cmd, ish)`.
  - Initializes either attach or detach command:
    - `nvme_init_ns_attach_ctrls()`
    - `nvme_init_ns_detach_ctrls()`
  - Executes via `libnvme_exec_admin_passthru()`.

Public wrappers:
- `nvme_namespace_attach_ctrls(...)`
- `nvme_namespace_detach_ctrls(...)`

Integration:
- Included in the nvme executable source list.
- Declared by `nvme-cmds.h`.
- Bridges CLI code to libnvme command initializer/executor APIs.

Risk and maintenance notes:
- `cmd` is not explicitly zero-initialized before possible `nvme_init_mi_cmd_flags()` and attach/detach initializer calls. Correctness depends on those initializers fully setting required fields or tolerating prior state.
