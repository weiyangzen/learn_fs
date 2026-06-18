# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-cmds.c

## Role

Implements higher-level libnvme command helpers that require command submission, multi-command log retrieval, allocation/reallocation, controller introspection, or computed transfer lengths.

## Initialization

A constructor `nvme_init_env()` reads `LIBNVME_FORCE_4K`. Values `1`, `true`, or strings beginning with `enable` force Get Log retrieval into 4 KiB chunks.

## Log Retrieval

- `submit_get_log_cmd()` prefers async admin passthrough if io_uring is available, and falls back to synchronous admin passthrough on `-ENOTSUP` or unavailable uring.
- `wait_get_log_cmd()` waits for async completion unless uring is unavailable.
- `libnvme_get_log()` chunks a Get Log Page request:
  - Preserves original LID/LSP and LSI fields.
  - Updates NUMD, RAE, LPO, data length, and buffer address per chunk.
  - Retains asynchronous events for all chunks except possibly the final one.
  - Honors forced 4 KiB mode.

## ANA Helpers

- `read_ana_chunk()` reads enough chunks to cover a requested pointer range.
- `try_read_ana()` walks ANA group descriptors, carefully avoiding misaligned descriptor dereference by copying `nnsids`.
- `libnvme_get_ana_log_atomic()` attempts atomic ANA log retrieval by checking `chgcnt` after multi-command reads and retrying on change.

## Host Behavior / Telemetry

- `libnvme_set_etdas()` and `libnvme_clear_etdas()` read Host Behavior feature, toggle ETDAS if needed, and report whether a change was made.
- `libnvme_get_uuid_list()` identifies the controller first and only fetches UUID list if the controller advertises UUID list support.
- `libnvme_get_telemetry_max()` identifies the controller and derives maximum telemetry data area plus max transfer size from MDTS.
- `libnvme_get_telemetry_log()` fetches telemetry header, computes requested data area size, reallocates, then fetches the full telemetry log.
- `libnvme_get_ctrl_telemetry()`, `libnvme_get_host_telemetry()`, and `libnvme_get_new_host_telemetry()` validate requested telemetry data area before fetching.

## Other Helpers

- `libnvme_get_lba_status_log()` performs two-stage LBA status log retrieval: initial header-sized read, then reallocates to reported full size.
- `libnvme_get_ana_log_len_from_id_ctrl()` computes maximum ANA log size from identify-controller data.
- `libnvme_get_ana_log_len()` identifies the controller and returns ANA log length estimate.
- `libnvme_get_logical_block_size()` identifies namespace, selects active LBA format from FLBAS, and returns `1 << ds`.
- `libnvme_get_feature_length()` maps feature IDs to required data payload lengths.
- `libnvme_get_directive_receive_length()` maps directive type/operation pairs to receive payload lengths.

## Dependencies

Uses endian helpers, min/max helpers, `libnvme.h`, and internal cleanup/private/compiler attributes headers. It depends heavily on inline initializers from the command headers.

## Notes

- `libnvme_get_log()` mutates the supplied passthrough command while chunking; callers should not expect the command to retain its original fields afterward.
- ANA atomic reading is careful about both changing log contents and misaligned packed data.
- Telemetry data area 4 support depends on controller capability and host behavior feature manipulation.
