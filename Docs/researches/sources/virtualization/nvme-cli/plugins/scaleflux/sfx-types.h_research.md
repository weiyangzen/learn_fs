# File Research: sources/virtualization/nvme-cli/plugins/scaleflux/sfx-types.h

ScaleFlux vendor type and constant definitions used by `sfx-nvme.c`.

Key constants:
- Vendor log IDs: latency read/write `0xc1`/`0xc3`, extended health `0xc2`, BBT `0xc7`, identify `0xcc`, alternate extended health `0xd2`.
- Feature IDs: atomic `0x01`, update provision capacity `0xac`, clean card `0xdc`.
- Vendor admin opcodes: query capacity `0xd3`, change capacity `0xd4`, set feature `0xd5`, get feature `0xd6`.
- Critical warning bits: power-fail data loss, over capacity, read/write lock.

Key structs:
- `sfx_freespace_ctx`: capacity/freespace fields in sector or 4 KiB units, map unit, max user space, and friendly capacity support.
- `nvme_additional_smart_log_item`: packed 12-byte-ish SMART item with normalized value and 6-byte raw payload, including union views for wear leveling and thermal throttling.
- `nvme_additional_smart_log`: ordered list of ScaleFlux additional SMART counters.
- `sfx_lat_stats_vanda` and `sfx_lat_stats_myrtle`: two firmware-generation-specific latency histogram layouts.
- `sfx_lat_stats`: union overlay allowing major/minor version probing before selecting the concrete layout.
- `extended_health_info_myrtle`: ScaleFlux extended health page fields used by status output, including OPN, physical capacity, compression ratio, power, IO speed, formatted capacity, and critical warning bits.

The file is pure shared layout. It must remain ABI-compatible with ScaleFlux firmware log/admin payloads.
