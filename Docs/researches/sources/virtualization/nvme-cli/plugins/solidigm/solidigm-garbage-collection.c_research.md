# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-garbage-collection.c

Solidigm vendor garbage collection log command implementation.

Main command:
- `solidigm_get_garbage_collection_log`: opens device, validates output format, gets the Solidigm UUID index via `sldgm_get_uuid_index`, retrieves vendor log ID `0xfd` with UUID index encoded into CDW14, then prints binary, JSON, or text.

Data layout:
- `gc_item`: `timer_type` plus `timestamp`.
- `garbage_control_collection_log`: version fields, 100 GC items, and reserved padding to fill the payload.

Output:
- Text prints device name, UUID index, and all 100 timestamp/timer-type entries.
- JSON emits an array of 100 entries with `timestamp` and `timer_type`.
- Binary dumps the full raw struct.

Dependencies:
- libnvme get-log passthrough.
- Solidigm UUID helper from `solidigm-util.h`.
