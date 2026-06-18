# File Research: sources/virtualization/nvme-cli/nvme-cmds.h

This header is nvme-cli's convenience command wrapper layer over libnvme passthrough command construction and execution. It is not the main NVMe command implementation; most functions allocate a local `struct libnvme_passthru_cmd`, call a `nvme_init_*()` helper from libnvme, then execute with `libnvme_exec_admin_passthru()`, `libnvme_exec_io_passthru()`, or `libnvme_get_log()`.

Primary command families:
- I/O command wrapper: `nvme_flush()` builds a flush command and executes it through the I/O passthrough path.
- Identify wrappers: generic `nvme_identify()` plus specific controller, active namespace list, namespace, CSI namespace, UUID list, namespace granularity, namespace descriptor list, and ZNS namespace identify helpers.
- Get Log wrappers: covers standard, NVM, ZNS, fabrics/discovery, telemetry, ANA, FDP, endurance, persistent-event, sanitize, SMART, lockdown, reachability, rotational media, power, physical interface, capacity, reservation, and related log pages.
- Feature wrappers: generic and simple `nvme_set_features()` / `nvme_set_features_simple()`, plus generic and simple `nvme_get_features()` / `nvme_get_features_simple()`.
- Namespace attach declarations: `nvme_namespace_attach_ctrls()` and `nvme_namespace_detach_ctrls()` are declared here and implemented in `nvme-cmds.c`.

Important behavior:
- The wrappers centralize common defaults such as `NVME_NSID_ALL`, `NVME_NSID_NONE`, `NVME_CSI_NVM`, fixed structure sizes, default `RAE` handling, and use of `NVME_LOG_PAGE_PDU_SIZE` for selected log pages.
- Result-producing feature commands copy `cmd.result` to the caller-provided `__u64 *result` only after command execution and only when the result pointer is non-null.
- Generic feature commands manually set passthrough fields beyond the initializer defaults, including namespace ID, cdw11-cdw15, data length, user buffer address, and UUID index encoding in cdw14.
- Variable-length log wrappers accept caller-provided lengths and offsets; fixed log wrappers commonly pass `sizeof(*log)`.

Integration role:
- Included by nvme-cli command code and plugins as the stable local shim for common libnvme commands.
- Depends directly on libnvme UAPI types, command enums, structure definitions, field encoding macros, and transport handle APIs.
- Allows plugin code to call concise command helpers such as `nvme_identify_ctrl()`, `nvme_get_log_smart()`, `nvme_get_features()`, and `nvme_set_features()` without hand-building passthrough command structs.

State and ownership:
- No persistent state is stored in this header.
- All command structs are stack-local.
- Caller owns all data buffers passed into identify, log, and feature commands.

Risk notes:
- This is a broad API surface; small changes can affect core nvme-cli commands and many vendor plugins.
- Wrapper correctness depends on exact NVMe command dword, namespace, log identifier, RAE, LSP, LSI, offset, length, and UUID-index semantics.
- Some parameters are only meaningful if forwarded correctly through either the local wrapper or the libnvme initializer. Audit carefully before edits, especially wrappers with `rae`, `nsid`, `len`, and offset parameters.
- The header exposes many `static inline` functions, so behavior changes compile into every caller rather than a single object file.
- Good tests should include representative identify, log, feature, namespace attach/detach, and plugin call paths, preferably with mocked passthrough command inspection where hardware is unavailable.
