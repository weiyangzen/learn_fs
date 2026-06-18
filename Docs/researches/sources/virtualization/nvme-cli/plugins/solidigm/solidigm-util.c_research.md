# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-util.c

Shared Solidigm helpers.

Defines:
- Solidigm UUID bytes.
- `sldgm_find_uuid_index()`: finds Solidigm UUID in an identify UUID list.
- `sldgm_get_uuid_index()`: fetches UUID list from the device and returns Solidigm index.
- `sldgm_dynamic_telemetry()`: fetches telemetry with decreasing transfer size on `-EPERM`.

Telemetry behavior:
- Starts max transfer at `(1 << mtds) * NVME_LOG_PAGE_PDU_SIZE`.
- Retries with half transfer size until success or minimum PDU size.
- Clears `create` after the first attempt.

Risks/notes:
- `sldgm_find_uuid_index()` returns `-errno` when UUID is not found, depending on libnvme behavior.
