# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdhtserial.c

Implements serialization and deserialization for traditional device halftones.

- Declares resident halftone resource list via `extern_gx_device_halftone_list`.
- Defines transfer-function serialization types:
  - none
  - identity
  - complete mapped table
- Defines halftone order type tags:
  - traditional
  - WTS
- `gx_ht_write_tf` serializes transfer maps:
  - one byte for none/identity
  - one byte plus mapped values for complete transfer tables
- `gx_ht_read_tf` reconstructs transfer maps and allocates `gx_transfer_map`.
- `gx_ht_write_component` serializes only the halftone order portion of a component.
  - Does not transmit component number or colorant name.
  - Rejects WTS orders as unsupported.
  - Omits reconstructible/runtime-only fields such as params, WTS enum, raster, original height/shift, full height, memory/cache, and screen params.
  - Encodes order procs as index into `ht_order_procs_table`.
  - Copies level and bit-data arrays verbatim.
- `gx_ht_read_component` reconstructs an order:
  - validates type and minimum encoded data
  - allocates level/bit-data arrays with `gx_ht_alloc_ht_order`
  - reads transfer function
  - compares against resident precompiled halftone resources
  - if resident data matches, frees transmitted arrays and points to ROM arrays
- `gx_ht_write` serializes a full multi-component halftone:
  - requires component array
  - writes halftone type and number of device components
  - serializes each component order
  - ignores `pdht->order`, rc/id, and LCM fields because renderer reconstructs them
- `gx_ht_read_and_install` reads a serialized halftone into stack component storage, then immediately installs it with `gx_imager_dev_ht_install`.
  - On failure, releases allocated component orders.
  - Combines read and install to avoid allocating a heap `gx_device_halftone` just to install and release it.

Limitations: WTS serialization is explicitly not implemented.
