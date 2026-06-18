# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-smart.c

Implements `smart-log-add`, which fetches Solidigm vendor SMART log page `0xca`.

Data model:
- `nvme_additional_smart_log_item` is a packed 12-byte item with id, normalized value, and 6-byte raw data.
- Special unions decode wear leveling, thermal throttle, and PLL/reference clock fields.
- `vu_smart_log` is a 512-byte page containing an array of items.

Main behavior:
- Maps SMART IDs to stable names via `id_to_name()`.
- Detects whether IDs `0xe7`/`0xe8` are present to disambiguate ID `0xc7` as `bad_tlp_error_count` versus `crc_error_count`.
- Prints normal tabular output, JSON output, or raw binary.
- Uses Solidigm UUID index in Get Log CDW14.

Special decoding:
- `0xad`: min/max/avg wear leveling.
- `0xea`: thermal throttle percentage and count.
- `0xf3`: PLL lock loss counters plus legacy raw value.
- Other IDs: 48-bit raw integer via `int48_to_long()`.

Risks/notes:
- Namespace option is parsed and displayed, but the Get Log command uses `NVME_NSID_ALL`.
- JSON keys use name mapping; unknown IDs collapse to `"unknown"`, so multiple unknown entries would overwrite each other.
